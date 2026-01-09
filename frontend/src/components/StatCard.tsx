'use client';

import { ReactNode } from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  trend?: {
    value: number;
    label: string;
  };
  loading?: boolean;
  className?: string; // Additional className for the container
  iconClassName?: string; // Class for the icon itself
  iconBgClassName?: string; // Class for the icon background
}

export default function StatCard({ 
  title, 
  value, 
  icon, 
  trend, 
  loading = false,
  className = "",
  iconClassName = "text-blue-600",
  iconBgClassName = "bg-blue-50"
}: StatCardProps) {
  if (loading) {
    return (
      <div className={`bg-white rounded-xl border border-slate-200 p-6 shadow-sm ${className}`}>
        <div className="animate-pulse flex items-start justify-between">
          <div className="space-y-3 w-full">
            <div className="h-4 bg-slate-100 rounded w-1/2"></div>
            <div className="h-8 bg-slate-100 rounded w-3/4"></div>
          </div>
          <div className="h-10 w-10 bg-slate-100 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow duration-200 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <div className="mt-2 flex items-baseline">
            <span className="text-2xl font-bold text-slate-900 tracking-tight">
              {value}
            </span>
            {trend && (
              <span className={`ml-2 text-xs font-medium px-2 py-0.5 rounded-full ${
                trend.value >= 0 
                  ? 'bg-emerald-50 text-emerald-700' 
                  : 'bg-red-50 text-red-700'
              }`}>
                {trend.value >= 0 ? '+' : ''}{trend.value}%
              </span>
            )}
          </div>
        </div>
        
        {icon && (
          <div className={`p-2.5 rounded-lg border border-transparent ${iconBgClassName} ${iconClassName}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}