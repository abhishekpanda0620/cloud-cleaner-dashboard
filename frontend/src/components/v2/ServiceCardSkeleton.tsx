import { Skeleton } from "@/components/Skeleton";

export default function ServiceCardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      {/* Service Name Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1 space-y-2">
           <div className="flex items-center justify-between">
              <Skeleton className="h-5 w-32" /> {/* Title */}
              <Skeleton className="h-4 w-16" /> {/* Category Badge */}
           </div>
           <Skeleton className="h-3 w-20" /> {/* Service Code */}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <Skeleton className="h-3 w-16 mb-2" /> {/* Label */}
          <Skeleton className="h-7 w-12" />      {/* Value */}
        </div>
        <div>
          <Skeleton className="h-3 w-20 mb-2" /> {/* Label */}
          <Skeleton className="h-7 w-24" />      {/* Value */}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
         <Skeleton className="h-6 w-32 rounded-full" /> {/* Status Badge */}
         <Skeleton className="h-4 w-4 rounded-full" />  {/* Arrow Icon */}
      </div>
    </div>
  );
}
