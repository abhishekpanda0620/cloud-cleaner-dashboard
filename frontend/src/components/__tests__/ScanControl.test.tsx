
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ScanControl from '../v2/ScanControl';
import { useScan } from '@/hooks/useScan';

// Mock the custom hook
jest.mock('@/hooks/useScan');

// Mock child components to isolate ScanControl logic
jest.mock('../RegionSelector', () => {
  return function DummyRegionSelector({ onRegionChange }: { onRegionChange: any }) {
    return (
      <div data-testid="region-selector">
        <button onClick={() => onRegionChange(['us-west-2'])}>Select West</button>
      </div>
    );
  };
});

describe('ScanControl Component', () => {
  const mockTriggerScan = jest.fn();
  
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    (useScan as jest.Mock).mockReturnValue({
      status: { is_scanning: false, started_at: null },
      loading: false,
      error: null,
      triggerScan: mockTriggerScan,
    });
  });

  it('renders correctly in idle state', () => {
    render(<ScanControl />);
    
    expect(screen.getByText('Resource Scanner')).toBeInTheDocument();
    expect(screen.getByText('Start Scan')).toBeInTheDocument();
    expect(screen.queryByText('Scanning...')).not.toBeInTheDocument();
  });

  it('triggers scan when button is clicked', async () => {
    render(<ScanControl />);
    
    const scanButton = screen.getByText('Start Scan');
    fireEvent.click(scanButton);
    
    await waitFor(() => {
      expect(mockTriggerScan).toHaveBeenCalledWith([], false);
    });
  });

  it('displays loading state when scanning', () => {
    (useScan as jest.Mock).mockReturnValue({
      status: { is_scanning: true, started_at: new Date().toISOString() },
      loading: false,
      error: null,
      triggerScan: mockTriggerScan,
    });

    render(<ScanControl />);
    
    // Check for scanning indicators
    expect(screen.getAllByText('Scanning...')).toHaveLength(2); // One in badget, one in button
    expect(screen.getByText('Analysing your AWS environment. This may take up to a minute.')).toBeInTheDocument();
    
    // Button should be disabled
    const button = screen.getByRole('button', { name: /scanning/i });
    expect(button).toBeDisabled();
  });

  it('displays error message when error occurs', () => {
    const errorMsg = 'Something went wrong';
    (useScan as jest.Mock).mockReturnValue({
      status: { is_scanning: false },
      loading: false,
      error: errorMsg,
      triggerScan: mockTriggerScan,
    });

    render(<ScanControl />);
    
    expect(screen.getByText(errorMsg)).toBeInTheDocument();
  });

  it('handles force scan via dropdown', async () => {
    render(<ScanControl />);
    
    // Open dropdown (ChevronDown icon button)
    // We can find it by the svg icon or closest button, let's use the container or simple click
    // The component has two buttons in the flex group. The second one is the dropdown toggle.
    const buttons = screen.getAllByRole('button');
    const dropdownToggle = buttons[2]; // 0 is region selector mock, 1 is scan, 2 is dropdown
    
    fireEvent.click(dropdownToggle);
    
    // Click "Force Deep Scan"
    const forceScanBtn = screen.getByText('Force Deep Scan');
    fireEvent.click(forceScanBtn);
    
    await waitFor(() => {
      expect(mockTriggerScan).toHaveBeenCalledWith([], true);
    });
  });

  it('handles region changes', () => {
    render(<ScanControl />);
    
    // Trigger mock region change
    const selectWestBtn = screen.getByText('Select West');
    fireEvent.click(selectWestBtn);
    
    // Now trigger scan, it should use the selected region
    const scanButton = screen.getByText('Start Scan');
    fireEvent.click(scanButton);
    
    expect(mockTriggerScan).toHaveBeenCalledWith(['us-west-2'], false);
  });
});
