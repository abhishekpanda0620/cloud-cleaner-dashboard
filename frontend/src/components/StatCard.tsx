interface StatCardProps {
  title: string;
  value: number | string;
  icon: string;
  bgColor: string;
  loading?: boolean;
}

export default function StatCard({ title, value, icon, bgColor, loading = false }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">
            {loading ? "..." : value}
          </p>
        </div>
        <div className={`h-12 w-12 ${bgColor} rounded-lg flex items-center justify-center`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  );
}