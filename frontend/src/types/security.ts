export interface SecurityFinding {
  id: number;
  check_id: string;
  check_name: string;
  severity: string;
  status: 'PASS' | 'FAIL' | 'WARNING';
  resource_id: string;
  resource_type?: string; 
  region: string;
  evidence: any; // Using any for flexibility with JSON evidence
  last_updated: string;
}

export interface SecurityStats {
  pass: number;
  fail: number;
  total: number;
  score: number;
}
