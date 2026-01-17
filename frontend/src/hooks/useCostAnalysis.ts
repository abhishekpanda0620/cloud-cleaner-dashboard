import { useState, useEffect } from 'react';
import { useNotifications } from '@/hooks/useNotifications';
import { CostAnalysisData, SavingsSummary } from '@/types/cost-analysis';

export function useCostAnalysis() {
  const [data, setData] = useState<CostAnalysisData>({
    estimates: [],
    trends: [],
    totalCurrentCost: 0,
    totalPotentialSavings: 0,
    totalResources: 0
  });
  const [savingsSummary, setSavingsSummary] = useState<SavingsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8084/api";
  const { notifications, addNotification, dismissNotification } = useNotifications();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [costRes, savingsRes] = await Promise.all([
          fetch(`${apiUrl}/cost-analysis`),
          fetch(`${apiUrl}/savings/summary`)
        ]);
        
        if (costRes.ok) {
          const costData = await costRes.json();
          setData(costData);
          setIsConnected(true);
        } else {
          throw new Error(`Failed to load cost data: ${costRes.statusText}`);
        }

        if (savingsRes.ok) {
          setSavingsSummary(await savingsRes.json());
        }

      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Failed to fetch data";
        setIsConnected(false);
        addNotification({
          type: 'error',
          title: 'Data Load Failed',
          message: errorMsg,
          duration: 6000
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [apiUrl, addNotification]);

  const handleExportPDF = async () => {
    try {
      const response = await fetch(`${apiUrl}/cost-analysis/export/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format: 'pdf' })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cost-analysis-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        addNotification({
          type: 'success',
          title: 'PDF Exported',
          message: 'Cost analysis report has been downloaded',
          duration: 4000
        });
      }
    } catch {
      addNotification({ type: 'error', title: 'Export Failed', message: 'Failed', duration: 3000 });
    }
  };

  const handleExportCSV = async () => {
    try {
        const response = await fetch(`${apiUrl}/cost-analysis/export/csv`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cost-analysis-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            addNotification({ type: 'success', title: 'CSV Exported', message: 'Done', duration: 3000 });
        }
    } catch(e) { console.error(e); }
  };

  return {
    data,
    savingsSummary,
    loading,
    isConnected,
    notifications,
    dismissNotification,
    handleExportPDF,
    handleExportCSV
  };
}
