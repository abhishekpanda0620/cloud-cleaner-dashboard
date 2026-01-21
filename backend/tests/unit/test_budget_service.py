
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from services.budget_service import BudgetService
from models.cost_limit import CostLimit

# Mock data
MOCK_AWS_BUDGETS = [{
    'BudgetName': 'Test AWS Budget',
    'BudgetLimit': {'Amount': '100.0', 'Unit': 'USD'},
    'CalculatedSpend': {'ActualSpend': {'Amount': '50.0'}},
    'TimePeriod': {'Start': '2023-01-01', 'End': '2023-01-31'}
}]

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_cost_explorer():
    with patch('services.budget_service.CostExplorerClient') as mock:
        client_instance = mock.return_value
        client_instance.get_cost_summary.return_value = {'total_cost': 45.0}
        yield client_instance

@pytest.fixture
def budget_service(mock_db, mock_cost_explorer):
    return BudgetService(mock_db)

@pytest.mark.asyncio
async def test_get_budgets_aws_priority(budget_service):
    """Test that AWS budgets are returned if they exist"""
    with patch.object(budget_service, '_get_aws_budgets', return_value=[{'name': 'AWS Budget', 'type': 'AWS'}]) as mock_aws:
        budgets = await budget_service.get_budgets()
        assert len(budgets) == 1
        assert budgets[0]['type'] == 'AWS'
        # Should not call native budget logic
        budget_service.db.execute.assert_not_called()

@pytest.mark.asyncio
async def test_get_budgets_native_fallback(budget_service):
    """Test fallback to native budget when AWS returns empty"""
    with patch.object(budget_service, '_get_aws_budgets', return_value=[]):
        # Mock DB returning a CostLimit
        mock_limit = CostLimit(amount=50.0, warning_threshold=80.0, alarm_threshold=100.0, currency='USD')
        
        # Mock the scalar_one_or_none result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_limit
        budget_service.db.execute.return_value = mock_result
        
        budgets = await budget_service.get_budgets()
        
        assert len(budgets) == 1
        assert budgets[0]['type'] == 'NATIVE'
        assert budgets[0]['limit'] == 50.0
        assert budgets[0]['current_spend'] == 45.0  # From mock_cost_explorer
        assert budgets[0]['percent_used'] == 90.0   # 45 / 50 * 100
        assert budgets[0]['status'] == 'WARNING'    # > 80%

@pytest.mark.asyncio
async def test_set_limit(budget_service):
    """Test setting a new local limit"""
    await budget_service.set_limit(150.0)
    
    # Should verify delete was called
    # Should verify add was called with new limit
    assert budget_service.db.add.called
    args = budget_service.db.add.call_args[0][0]
    assert isinstance(args, CostLimit)
    assert args.amount == 150.0
