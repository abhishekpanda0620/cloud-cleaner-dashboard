import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import Logo from '@/components/Logo';

export default function SignIn() {
  return (
    <div className="sm:mx-auto sm:w-full sm:max-w-md">
      <div className="flex justify-center mb-6">
        <Link href="/" className="flex items-center gap-2 group">
           <Logo className="w-10 h-10" />
           <span className="font-bold text-2xl text-slate-900 tracking-tight">Cloud Cleaner</span>
        </Link>
      </div>

      <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-slate-200">
        <div className="space-y-6">
          <div>
            <h2 className="text-center text-xl font-bold tracking-tight text-slate-900">
              Sign in to your account
            </h2>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-2 text-slate-500">Demo Access</span>
            </div>
          </div>

          <Link
            href="/dashboard"
            className="flex w-full justify-center rounded-lg border border-transparent bg-slate-900 py-2.5 px-4 text-sm font-medium text-white shadow-sm hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 transition-all group"
          >
            <span className="flex items-center gap-2">
              Continue as Guest <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </span>
          </Link>
          
          <p className="text-xs text-center text-slate-500 mt-4">
            By continuing, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
}
