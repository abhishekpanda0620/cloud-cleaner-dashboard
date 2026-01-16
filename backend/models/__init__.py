from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from core.config import settings

Base = declarative_base()

# Import models to register them with Base
from .service import AWSService
from .resource import Resource
from .cost_history import CostHistory
from .scan_history import ScanHistory
from .savings_history import SavingsHistory
from .security import SecurityFramework, SecurityControl, SecurityCheck, SecurityFinding

# Create async engine
# Create async engine
# Use NullPool to avoid asyncio loop issues with Celery/multiprocessing
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    poolclass=NullPool
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)