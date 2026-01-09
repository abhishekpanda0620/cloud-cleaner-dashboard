import Link from "next/link";
import Image from "next/image";
import { ArrowRight, Cloud, Shield, DollarSign, BarChart2, CheckCircle2, Zap, Layout, PlayCircle } from "lucide-react";
import Logo from "@/components/Logo";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 selection:bg-blue-100 selection:text-blue-900 font-inter">
      {/* Navbar - Glassmorphism */}
      <nav className="fixed w-full border-b border-white/20 bg-white/70 backdrop-blur-xl z-50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-2 group cursor-pointer">
              <div className="relative w-8 h-8">
                <div className="absolute inset-0 bg-blue-500 blur-lg opacity-20 group-hover:opacity-40 transition-opacity rounded-lg"></div>
                 <Logo className="relative w-8 h-8" />
              </div>
              <span className="font-bold text-xl text-slate-900 tracking-tight ml-2">Cloud Cleaner</span>
            </div>
            <div className="flex items-center gap-4">
              <Link 
                href="/signin"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors px-3 py-2 rounded-md hover:bg-slate-50"
              >
                Sign In
              </Link>
              <Link 
                href="/signin"
                className="group relative bg-slate-900 text-white px-5 py-2 rounded-full text-sm font-medium shadow-lg hover:shadow-xl hover:bg-slate-800 transition-all flex items-center gap-2 overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-2">
                  Get Started <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden pt-32 pb-40">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light"></div>
        
        {/* Animated Background Gradients */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-blue-200/50 rounded-full blur-[100px] opacity-40 -z-10 animate-pulse-slow"></div>
        <div className="absolute bottom-0 right-0 w-[600px] h-[400px] bg-purple-200/50 rounded-full blur-[100px] opacity-40 -z-10 delay-1000 animate-pulse-slow"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
           <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
             
             {/* Headline */}
             <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 mb-6 leading-[1.1]">
               Automate your cloud <br/>
               <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 animate-gradient-x">
                 cost intelligence
               </span>
             </h1>
             
             <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
               Instant visibility into unused resources, cost anomalies, and optimization opportunities. Save up to 30% on your AWS bill in minutes.
             </p>

             {/* Buttons */}
             <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
                <Link 
                  href="/dashboard"
                  className="w-full sm:w-auto px-8 py-4 bg-slate-900 text-white rounded-2xl font-semibold text-lg hover:bg-slate-800 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-1 flex items-center justify-center gap-2 group ring-4 ring-slate-100 ring-offset-2 ring-offset-transparent"
                >
                  <Layout className="w-5 h-5 text-blue-300 group-hover:text-white transition-colors" />
                  Launch Dashboard
                </Link>
                <Link 
                  href="/cost-analysis"
                  className="w-full sm:w-auto px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-2xl font-semibold text-lg hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm hover:shadow-md flex items-center justify-center gap-2"
                >
                  <PlayCircle className="w-5 h-5 text-slate-400" />
                  View Demo
                </Link>
             </div>

             {/* Mockup / Visual */}
             <div className="mt-20 relative w-full max-w-5xl mx-auto perspective-1000">
                <div className="relative rounded-2xl bg-slate-900/5 p-2 backdrop-blur-sm border border-slate-200/50 shadow-2xl transform rotate-x-12 translate-y-6 hover:translate-y-2 hover:rotate-x-6 transition-all duration-700 ease-out">
                   <div className="rounded-xl overflow-hidden bg-white shadow-inner border border-slate-100">
                      {/* Fake generic UI mockup */}
                       <div className="h-10 bg-slate-50 border-b border-slate-100 flex items-center px-4 gap-2">
                          <div className="flex gap-1.5">
                             <div className="w-3 h-3 rounded-full bg-red-400/80"></div>
                             <div className="w-3 h-3 rounded-full bg-amber-400/80"></div>
                             <div className="w-3 h-3 rounded-full bg-emerald-400/80"></div>
                          </div>
                       </div>
                       <div className="grid grid-cols-12 gap-0 h-[400px]">
                          <div className="col-span-2 border-r border-slate-100 bg-slate-50/50 p-4 space-y-3">
                             <div className="h-8 rounded bg-slate-200/50 w-full animate-pulse"></div>
                             <div className="h-8 rounded bg-slate-200/50 w-3/4 animate-pulse delay-75"></div>
                             <div className="h-8 rounded bg-slate-200/50 w-5/6 animate-pulse delay-150"></div>
                          </div>
                          <div className="col-span-10 p-6 bg-white">
                             <div className="flex justify-between items-center mb-6">
                                <div className="h-8 rounded bg-slate-100 w-1/3"></div>
                                <div className="flex gap-2">
                                   <div className="h-8 w-24 rounded bg-blue-50"></div>
                                   <div className="h-8 w-8 rounded bg-slate-100"></div>
                                </div>
                             </div>
                             <div className="grid grid-cols-3 gap-6 mb-8">
                                <div className="h-32 rounded-xl bg-blue-50/50 border border-blue-100 shadow-sm"></div>
                                <div className="h-32 rounded-xl bg-purple-50/50 border border-purple-100 shadow-sm"></div>
                                <div className="h-32 rounded-xl bg-emerald-50/50 border border-emerald-100 shadow-sm"></div>
                             </div>
                             <div className="h-48 rounded-xl bg-slate-50 border border-slate-100"></div>
                          </div>
                       </div>
                   </div>
                   
                   {/* Floating Cards */}
                   <div className="absolute -right-8 -top-8 bg-white p-4 rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-slate-100 animate-float">
                      <div className="flex items-center gap-3">
                         <div className="p-2 bg-green-100 rounded-lg text-green-600"><DollarSign className="w-5 h-5" /></div>
                         <div>
                            <p className="text-xs text-slate-500 font-medium">Monthly Savings</p>
                            <p className="text-lg font-bold text-slate-900">$1,240.50</p>
                         </div>
                      </div>
                   </div>
                   
                   <div className="absolute -left-8 top-20 bg-white p-4 rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-slate-100 animate-float-delayed">
                      <div className="flex items-center gap-3">
                         <div className="p-2 bg-red-100 rounded-lg text-red-600"><Zap className="w-5 h-5" /></div>
                         <div>
                            <p className="text-xs text-slate-500 font-medium">Idle Resources</p>
                            <p className="text-lg font-bold text-slate-900">12 Found</p>
                         </div>
                      </div>
                   </div>
                </div>
             </div>
           </div>
        </div>
      </div>

      {/* Bento Grid Features */}
      <div className="py-24 bg-white relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
             <h2 className="text-3xl font-bold text-slate-900 mb-4">Everything you need to optimize</h2>
             <p className="text-lg text-slate-500">
               Powerful features wrapped in a beautiful, intuitive interface. Designed for engineering teams who care about craftsmanship.
             </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">
             
             {/* Large Card 1 */}
             <div className="md:col-span-2 row-span-1 bg-slate-50 rounded-2xl border border-slate-200 p-8 flex flex-col justify-between hover:border-blue-200 hover:shadow-lg transition-all group overflow-hidden relative">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-100/50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 opacity-0 group-hover:opacity-50 transition-opacity"></div>
                <div className="relative z-10">
                   <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mb-4 shadow-lg shadow-blue-200">
                      <Shield className="w-5 h-5 text-white" />
                   </div>
                   <h3 className="text-xl font-bold text-slate-900 mb-2">Secure Read-Only Access</h3>
                   <p className="text-slate-600 max-w-md">Our agent uses a confined IAM role with `ReadOnlyAccess`. We scan your infrastructure without creating risks or modifying resources without explicit approval.</p>
                </div>
             </div>

             {/* Tall Card */}
             <div className="md:col-span-1 row-span-2 bg-slate-900 rounded-2xl border border-slate-800 p-8 flex flex-col justify-between relative overflow-hidden group text-white">
                <div className="absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-900"></div>
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay"></div>
                <div className="relative z-10 h-full flex flex-col">
                   <div className="w-10 h-10 bg-slate-700/50 backdrop-blur-md border border-slate-600 rounded-lg flex items-center justify-center mb-4">
                      <BarChart2 className="w-5 h-5 text-blue-400" />
                   </div>
                   <h3 className="text-xl font-bold mb-2">Real-time Analytics</h3>
                   <p className="text-slate-400 text-sm mb-6">Live dashboards showing usage trends, cost spikes, and efficient resource allocation.</p>
                   
                   <div className="mt-auto bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                      <div className="flex justify-between items-end gap-2 h-24">
                         <div className="w-1/4 bg-blue-500/30 rounded-t h-[40%]"></div>
                         <div className="w-1/4 bg-blue-500/50 rounded-t h-[60%]"></div>
                         <div className="w-1/4 bg-blue-500/70 rounded-t h-[30%]"></div>
                         <div className="w-1/4 bg-blue-500 rounded-t h-[80%]"></div>
                      </div>
                   </div>
                </div>
             </div>

             {/* Small Card */}
             <div className="md:col-span-1 row-span-1 bg-white rounded-2xl border border-slate-200 p-8 hover:border-emerald-200 hover:shadow-lg transition-all group overflow-hidden">
                <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center mb-4 text-emerald-600">
                   <DollarSign className="w-5 h-5" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Cost Intelligence</h3>
                <p className="text-sm text-slate-600">Identify unattached EBS volumes and idle EC2 instances instantly.</p>
             </div>

             {/* Small Card */}
             <div className="md:col-span-1 row-span-1 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100 p-8 hover:shadow-lg transition-all">
                <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 text-indigo-600">
                   <CheckCircle2 className="w-5 h-5" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">One-Click Cleanup</h3>
                <p className="text-sm text-slate-600">Generated remediation scripts and direct deletion from the UI.</p>
             </div>

          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-50 border-t border-slate-200 py-12">
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
               <Cloud className="w-5 h-5 text-slate-400" />
               <p className="text-slate-500 text-sm font-medium">
                 © {new Date().getFullYear()} Cloud Cleaner.
               </p>
            </div>
            <div className="flex gap-8 text-sm">
               <a href="#" className="text-slate-500 hover:text-slate-900 transition-colors">Github</a>
               <a href="#" className="text-slate-500 hover:text-slate-900 transition-colors">Documentation</a>
               <a href="#" className="text-slate-500 hover:text-slate-900 transition-colors">Twitter</a>
            </div>
         </div>
      </footer>
    </div>
  );
}
