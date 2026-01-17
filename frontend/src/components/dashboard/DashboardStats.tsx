import { Package, AlertTriangle, Search } from 'lucide-react';
import StatCard from '@/components/StatCard';

interface DashboardStatsProps {
  summary: any;
  loading: boolean;
  serviceCount: number;
  servicesLoading: boolean;
}

export function DashboardStats({ summary, loading, serviceCount, servicesLoading }: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatCard
        title="Total Resources"
        value={summary?.total_resources || 0}
        icon={<Package className="w-5 h-5" />}
        loading={loading}
        iconClassName="text-blue-500"
        iconBgClassName="bg-blue-50"
      />
      <StatCard
        title="Unused Resources"
        value={summary?.unused_resources || 0}
        icon={<AlertTriangle className="w-5 h-5" />}
        loading={loading}
        iconClassName="text-amber-500"
        iconBgClassName="bg-amber-50"
      />
      <StatCard
        title="Services"
        value={serviceCount}
        icon={<Search className="w-5 h-5" />}
        loading={servicesLoading}
        iconClassName="text-purple-500"
        iconBgClassName="bg-purple-50"
      />
    </div>
  );
}
