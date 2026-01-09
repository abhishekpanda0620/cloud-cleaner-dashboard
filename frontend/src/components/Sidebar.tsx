'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, PieChart, Settings, Cloud } from 'lucide-react';
import Logo from '@/components/Logo';

export default function Sidebar() {
  const pathname = usePathname();

  const navigation = [
    { name: 'Resources', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Cost Analysis', href: '/cost-analysis', icon: PieChart },
  ];

  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-screen shrink-0 border-r border-slate-800">
      <div className="p-6 flex items-center gap-3 border-b border-slate-800">
        <Logo className="w-8 h-8" />
        <div>
          <h1 className="font-bold text-lg leading-tight">Cloud Cleaner</h1>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <Link 
          href="/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 w-full transition-colors"
        >
          <Settings className="w-5 h-5" />
          Settings
        </Link>
      </div>
    </div>
  );
}
