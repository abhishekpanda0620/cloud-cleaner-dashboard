import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="text-center mb-16 animate-fade-in">
          <div className="flex items-center justify-center mb-6">
            <div className="h-20 w-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl transform hover:scale-110 transition-transform duration-300">
              <span className="text-5xl">☁️</span>
            </div>
          </div>
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-6">
            Cloud Cleaner
          </h1>
          <p className="text-xl text-slate-700 max-w-3xl mx-auto leading-relaxed">
            Monitor, analyze, and optimize your AWS resources with intelligent cost analysis and automated cleanup
          </p>
          <div className="mt-8 flex items-center justify-center gap-4">
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-green-100 text-green-800 shadow-md">
              <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse mr-2"></span>
              Production Ready
            </span>
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-800 shadow-md">
              Version 0.4.0
            </span>
          </div>
        </div>

        {/* Dashboard Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {/* Resource Dashboard Card */}
          <Link href="/dashboard" className="group">
            <div className="relative overflow-hidden bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl shadow-2xl p-8 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -mr-20 -mt-20"></div>
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/10 rounded-full -ml-16 -mb-16"></div>
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <div className="h-20 w-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-xl">
                    <span className="text-4xl">🖥️</span>
                  </div>
                  <div className="text-white group-hover:translate-x-2 transition-transform duration-300">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
                <h2 className="text-3xl font-bold text-white mb-4 drop-shadow-lg">
                  Resource Dashboard
                </h2>
                <p className="text-white/90 mb-6 text-lg leading-relaxed">
                  Monitor and manage your AWS resources including EC2 instances, EBS volumes, S3 buckets, and IAM resources
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">EC2</span>
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">EBS</span>
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">S3</span>
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">IAM</span>
                </div>
              </div>
            </div>
          </Link>

          {/* Cost Analysis Card */}
          <Link href="/cost-analysis" className="group">
            <div className="relative overflow-hidden bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl shadow-2xl p-8 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -mr-20 -mt-20"></div>
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/10 rounded-full -ml-16 -mb-16"></div>
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <div className="h-20 w-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-xl">
                    <span className="text-4xl">💰</span>
                  </div>
                  <div className="text-white group-hover:translate-x-2 transition-transform duration-300">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
                <h2 className="text-3xl font-bold text-white mb-4 drop-shadow-lg">
                  Cost Analysis
                </h2>
                <p className="text-white/90 mb-6 text-lg leading-relaxed">
                  Track costs, identify savings opportunities, and generate detailed reports with cost breakdowns and trends
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">Savings</span>
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">Reports</span>
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">Trends</span>
                  <span className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30">Export</span>
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Features Section */}
        <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl border border-slate-200/50 p-10">
          <h2 className="text-3xl font-bold text-slate-900 mb-8 text-center">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Key Features
            </span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="group text-center p-6 rounded-2xl hover:bg-blue-50 transition-all duration-300 transform hover:-translate-y-1">
              <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">🔍</span>
              </div>
              <h3 className="font-bold text-slate-900 mb-3 text-lg">Resource Scanning</h3>
              <p className="text-slate-600 leading-relaxed">
                Automatically detect unused and underutilized AWS resources
              </p>
            </div>
            <div className="group text-center p-6 rounded-2xl hover:bg-emerald-50 transition-all duration-300 transform hover:-translate-y-1">
              <div className="h-16 w-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">💸</span>
              </div>
              <h3 className="font-bold text-slate-900 mb-3 text-lg">Cost Optimization</h3>
              <p className="text-slate-600 leading-relaxed">
                Calculate potential savings and track cost trends over time
              </p>
            </div>
            <div className="group text-center p-6 rounded-2xl hover:bg-purple-50 transition-all duration-300 transform hover:-translate-y-1">
              <div className="h-16 w-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">📊</span>
              </div>
              <h3 className="font-bold text-slate-900 mb-3 text-lg">Detailed Reports</h3>
              <p className="text-slate-600 leading-relaxed">
                Export comprehensive reports in PDF and CSV formats
              </p>
            </div>
            <div className="group text-center p-6 rounded-2xl hover:bg-orange-50 transition-all duration-300 transform hover:-translate-y-1">
              <div className="h-16 w-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">🔔</span>
              </div>
              <h3 className="font-bold text-slate-900 mb-3 text-lg">Smart Notifications</h3>
              <p className="text-slate-600 leading-relaxed">
                Get alerts via email and Slack for important resource changes
              </p>
            </div>
            <div className="group text-center p-6 rounded-2xl hover:bg-red-50 transition-all duration-300 transform hover:-translate-y-1">
              <div className="h-16 w-16 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">⏰</span>
              </div>
              <h3 className="font-bold text-slate-900 mb-3 text-lg">Scheduled Scans</h3>
              <p className="text-slate-600 leading-relaxed">
                Automate resource scanning with customizable schedules
              </p>
            </div>
            <div className="group text-center p-6 rounded-2xl hover:bg-indigo-50 transition-all duration-300 transform hover:-translate-y-1">
              <div className="h-16 w-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">🗑️</span>
              </div>
              <h3 className="font-bold text-slate-900 mb-3 text-lg">Safe Cleanup</h3>
              <p className="text-slate-600 leading-relaxed">
                Delete unused resources safely with confirmation dialogs
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/80 backdrop-blur-md rounded-full shadow-lg border border-slate-200/50">
            <span className="text-slate-600 text-sm font-medium">Built with</span>
            <span className="px-3 py-1 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full text-xs font-semibold">Next.js</span>
            <span className="px-3 py-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-full text-xs font-semibold">FastAPI</span>
            <span className="px-3 py-1 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-full text-xs font-semibold">AWS SDK</span>
          </div>
        </div>
      </div>
    </div>
  );
}
