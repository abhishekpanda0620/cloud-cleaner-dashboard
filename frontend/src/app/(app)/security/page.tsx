'use client';

import { ShieldCheck } from 'lucide-react';

export default function SecurityPage() {
  return (
    <div className="min-h-full">
      {/* Header matching DashboardV2 */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-slate-100 p-2 rounded-lg border border-slate-200">
               <ShieldCheck className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-slate-900 leading-tight">
                Security & Compliance
              </h1>
              <p className="text-sm text-slate-500">
                Audit-ready security posture management
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content matching DashboardV2 spacing */}
      <main className="px-6 py-8 space-y-8">
        
        {/* Placeholder / Coming Soon State */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 p-8 rounded-xl bg-white border border-slate-200 shadow-sm">
             <div className="h-64 flex flex-col items-center justify-center text-slate-500">
                <div className="bg-indigo-50 p-4 rounded-full mb-4">
                    <ShieldCheck className="w-12 h-12 text-indigo-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900">Security Frameworks Initializing</h3>
                <p className="text-sm text-slate-500 mt-2 max-w-sm text-center">
                  We are currently implementing the CIS AWS Foundations Benchmark scanners. Check back soon for your compliance score.
                </p>
             </div>
          </div>

          {/* Supported Frameworks Card */}
          <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
            <h3 className="font-semibold text-slate-900 mb-4 border-b border-slate-100 pb-2">
                Active Frameworks
            </h3>
            <ul className="space-y-4">
               <li className="flex items-start gap-3">
                  <div className="mt-1 w-2 h-2 rounded-full bg-green-500 shrink-0"></div>
                  <div>
                      <p className="text-sm font-medium text-slate-900">CIS AWS Foundations v1.4.0</p>
                      <p className="text-xs text-slate-500">Scanning enabled (Phase 1)</p>
                  </div>
               </li>
               <li className="flex items-start gap-3">
                  <div className="mt-1 w-2 h-2 rounded-full bg-slate-300 shrink-0"></div>
                   <div>
                      <p className="text-sm font-medium text-slate-400">SOC 2 (Trust Services)</p>
                      <p className="text-xs text-slate-400">Planned (Phase 2)</p>
                  </div>
               </li>
               <li className="flex items-start gap-3">
                  <div className="mt-1 w-2 h-2 rounded-full bg-slate-300 shrink-0"></div>
                   <div>
                      <p className="text-sm font-medium text-slate-400">HIPAA</p>
                      <p className="text-xs text-slate-400">Planned (Phase 2)</p>
                  </div>
               </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
