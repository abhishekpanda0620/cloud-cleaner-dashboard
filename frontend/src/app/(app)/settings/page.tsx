import { User, Settings as SettingsIcon, Shield, Bell, Key } from 'lucide-react';

export default function Settings() {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500">Manage your account settings and preferences.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <div className="space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium">
            <User className="w-4 h-4" />
            General
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-50 rounded-lg text-sm font-medium transition-colors">
            <Key className="w-4 h-4" />
            API Keys
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-50 rounded-lg text-sm font-medium transition-colors">
            <Bell className="w-4 h-4" />
            Notifications
          </button>
        </div>

        {/* Settings Content */}
        <div className="md:col-span-3 space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2 bg-slate-50/50">
              <User className="w-5 h-5 text-slate-500" />
              <h2 className="font-semibold text-slate-900">Profile Information</h2>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                    <input type="text" defaultValue="Guest User" className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" />
                 </div>
                 <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                    <input type="email" defaultValue="guest@cloudcleaner.app" className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" />
                 </div>
              </div>
            </div>
            <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 text-right">
               <button className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors">Save Changes</button>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2 bg-slate-50/50">
              <Shield className="w-5 h-5 text-slate-500" />
              <h2 className="font-semibold text-slate-900">AWS Configuration</h2>
            </div>
            <div className="p-6 space-y-4">
              <div className="rounded-lg bg-amber-50 border border-amber-100 p-4">
                 <div className="flex gap-3">
                    <Shield className="w-5 h-5 text-amber-600 shrink-0" />
                    <div>
                       <h3 className="text-sm font-bold text-amber-900">Read-Only Access</h3>
                       <p className="text-sm text-amber-700 mt-1">This demo environment uses simulated AWS data. No actual AWS credentials are required.</p>
                    </div>
                 </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
