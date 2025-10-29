import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            ☁️ Cloud Cleaner 🧹
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Monitor, analyze, and optimize your AWS resources with intelligent cost analysis and automated cleanup
          </p>
        </div>

        {/* Dashboard Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {/* Resource Dashboard Card */}
          <Link href="/dashboard">
            <div className="bg-white rounded-2xl shadow-lg border-2 border-slate-200 p-8 hover:shadow-xl hover:border-blue-400 transition-all cursor-pointer group">
              <div className="flex items-center justify-between mb-6">
                <div className="h-16 w-16 bg-blue-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-3xl">🖥️</span>
                </div>
                <div className="text-blue-500 group-hover:translate-x-1 transition-transform">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">
                Resource Dashboard
              </h2>
              <p className="text-slate-600 mb-4">
                Monitor and manage your AWS resources including EC2 instances, EBS volumes, S3 buckets, and IAM resources
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">EC2</span>
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">EBS</span>
                <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">S3</span>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">IAM</span>
              </div>
            </div>
          </Link>

          {/* Cost Analysis Card */}
          <Link href="/cost-analysis">
            <div className="bg-white rounded-2xl shadow-lg border-2 border-slate-200 p-8 hover:shadow-xl hover:border-emerald-400 transition-all cursor-pointer group">
              <div className="flex items-center justify-between mb-6">
                <div className="h-16 w-16 bg-emerald-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-3xl">💰</span>
                </div>
                <div className="text-emerald-500 group-hover:translate-x-1 transition-transform">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">
                Cost Analysis
              </h2>
              <p className="text-slate-600 mb-4">
                Track costs, identify savings opportunities, and generate detailed reports with cost breakdowns and trends
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium">Savings</span>
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">Reports</span>
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">Trends</span>
                <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">Export</span>
              </div>
            </div>
          </Link>
        </div>

        {/* Features Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6 text-center">
            Key Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🔍</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Resource Scanning</h3>
              <p className="text-sm text-slate-600">
                Automatically detect unused and underutilized AWS resources
              </p>
            </div>
            <div className="text-center">
              <div className="h-12 w-12 bg-emerald-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">💸</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Cost Optimization</h3>
              <p className="text-sm text-slate-600">
                Calculate potential savings and track cost trends over time
              </p>
            </div>
            <div className="text-center">
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Detailed Reports</h3>
              <p className="text-sm text-slate-600">
                Export comprehensive reports in PDF and CSV formats
              </p>
            </div>
            <div className="text-center">
              <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🔔</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Smart Notifications</h3>
              <p className="text-sm text-slate-600">
                Get alerts via email and Slack for important resource changes
              </p>
            </div>
            <div className="text-center">
              <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">⏰</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Scheduled Scans</h3>
              <p className="text-sm text-slate-600">
                Automate resource scanning with customizable schedules
              </p>
            </div>
            <div className="text-center">
              <div className="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🗑️</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Safe Cleanup</h3>
              <p className="text-sm text-slate-600">
                Delete unused resources safely with confirmation dialogs
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-slate-600">
          <p className="text-sm">
            Built with Next.js, FastAPI, and AWS SDK • Version 0.4.0
          </p>
        </div>
      </div>
    </div>
  );
}
