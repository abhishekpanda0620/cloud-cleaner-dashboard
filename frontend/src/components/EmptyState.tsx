interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
}

export default function EmptyState({ icon, title, description }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <span className="text-6xl mb-4 block">{icon}</span>
      <p className="text-slate-600 text-lg font-medium">{title}</p>
      <p className="text-slate-500 text-sm mt-2">{description}</p>
    </div>
  );
}