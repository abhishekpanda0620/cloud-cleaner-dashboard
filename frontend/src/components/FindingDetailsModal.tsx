import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { CheckCircle, XCircle, AlertTriangle, Shield } from "lucide-react";

interface FindingDetailsModalProps {
  finding: any;
  isOpen: boolean;
  onClose: () => void;
}

export function FindingDetailsModal({ finding, isOpen, onClose }: FindingDetailsModalProps) {
  if (!finding) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Shield className="w-5 h-5 text-indigo-600" />
            Finding Details
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Status Header */}
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-100">
            <div>
              <h3 className="font-semibold text-slate-900">{finding.check_name}</h3>
              <p className="text-sm text-slate-500 font-mono mt-1">{finding.check_id}</p>
            </div>
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${
               finding.status === 'PASS' 
                ? 'bg-green-50 text-green-700 border-green-200' 
                : finding.status === 'FAIL'
                ? 'bg-red-50 text-red-700 border-red-200'
                : 'bg-yellow-50 text-yellow-700 border-yellow-200'
            }`}>
               {finding.status === 'PASS' && <CheckCircle className="w-4 h-4" />}
               {finding.status === 'FAIL' && <XCircle className="w-4 h-4" />}
               <span className="font-semibold text-sm">{finding.status}</span>
            </div>
          </div>

          {/* Core Info Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 border border-slate-200 rounded-lg">
                <span className="text-xs text-slate-500 uppercase font-semibold">Severity</span>
                <p className={`mt-1 font-medium ${
                    finding.severity === 'Critical' ? 'text-red-600' :
                    finding.severity === 'High' ? 'text-orange-600' : 'text-slate-700'
                }`}>{finding.severity}</p>
            </div>
            <div className="p-3 border border-slate-200 rounded-lg">
                <span className="text-xs text-slate-500 uppercase font-semibold">Region</span>
                <p className="mt-1 font-medium text-slate-900">{finding.region}</p>
            </div>
             <div className="p-3 border border-slate-200 rounded-lg col-span-2">
                <span className="text-xs text-slate-500 uppercase font-semibold">Affected Resource</span>
                <p className="mt-1 font-medium text-slate-900">{finding.resource_id}</p>
                <p className="text-xs text-slate-500">{finding.resource_type}</p>
            </div>
          </div>

          {/* Evidence Section */}
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-2">Technical Evidence</h4>
            <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-xs text-slate-50 font-mono">
                {JSON.stringify(finding.evidence, null, 2)}
              </pre>
            </div>
          </div>

          {/* Remediation (Placeholder logic as we don't have remediation text in Finding object yet, usually in Check def) */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
             <h4 className="text-sm font-semibold text-blue-900 mb-1">Remediation</h4>
             <p className="text-sm text-blue-700">
                Review the evidence above. Consult the CIS AWS Foundations Benchmark v1.4.0 documentation for control 
                <span className="font-mono font-bold mx-1">{finding.check_id.replace('check_', '').replace('_', '-')}</span> 
                remediation steps.
             </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
