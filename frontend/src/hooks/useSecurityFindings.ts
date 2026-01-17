import { useState, useEffect, useMemo, useCallback } from 'react';
import { SecurityStats, SecurityFinding } from '@/types/security';

export function useSecurityFindings() {
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [findings, setFindings] = useState<SecurityFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [statsRes, findingsRes] = await Promise.all([
        fetch(`${apiUrl}/security/stats`),
        fetch(`${apiUrl}/security/findings`)
      ]);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (findingsRes.ok) setFindings(await findingsRes.json());
    } catch (error) {
      console.error("Failed to fetch security data", error);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const triggerScan = async () => {
    try {
      setScanning(true);
      await fetch(`${apiUrl}/security/scan`, { method: 'POST' });
      await fetchData();
    } catch (error) {
      console.error("Scan failed", error);
    } finally {
      setScanning(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Hook for filtering/sorting
  const useFilteredFindings = (
    searchQuery: string, 
    statusFilter: 'ALL' | 'PASS' | 'FAIL', 
    sortOrder: 'severity_desc' | 'severity_asc'
  ) => {
    return useMemo(() => {
        let result = findings.filter(f => {
           const matchesSearch = 
            f.check_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            f.resource_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
            f.severity.toLowerCase().includes(searchQuery.toLowerCase()) ||
            f.check_id.toLowerCase().includes(searchQuery.toLowerCase());
           
           const matchesStatus = statusFilter === 'ALL' || f.status === statusFilter;
           
           return matchesSearch && matchesStatus;
        });
    
        const severityWeight = { 'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
        
        result.sort((a, b) => {
            const weightA = severityWeight[a.severity as keyof typeof severityWeight] || 0;
            const weightB = severityWeight[b.severity as keyof typeof severityWeight] || 0;
            
            if (sortOrder === 'severity_desc') {
                return weightB - weightA;
            } else {
                return weightA - weightB;
            }
        });
    
        return result;
      }, [findings, searchQuery, statusFilter, sortOrder]);
  };

  return {
    stats,
    findings,
    loading,
    scanning,
    triggerScan,
    useFilteredFindings,
    apiUrl
  };
}
