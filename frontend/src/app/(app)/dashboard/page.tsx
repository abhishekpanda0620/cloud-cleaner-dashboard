'use client';

import { useDashboard } from '@/hooks/useDashboard';
import ScanControl from '@/components/v2/ScanControl';
import ServiceGrid from '@/components/v2/ServiceGrid';
import ServiceResourceView from '@/components/v2/ServiceResourceView';
import NotificationCenter from '@/components/NotificationCenter';
import ResourceDetailsModal from '@/components/ResourceDetailsModal';
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal';
import ScheduleSettings from '@/components/ScheduleSettings';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { DashboardStats } from '@/components/dashboard/DashboardStats';

export default function DashboardV2() {
  const {
    selectedService,
    selectedRegions,
    setSelectedRegions,
    detailsModal,
    setDetailsModal,
    deleteModal,
    setDeleteModal,
    notifications,
    services,
    servicesLoading,
    servicesError,
    summary,
    summaryLoading,
    apiUrl,
    handleServiceClick,
    handleBackToServices,
    handleViewDetails,
    handleDelete,
    handleConfirmDelete,
    handleScanComplete,
    dismissNotification
  } = useDashboard();

  return (
    <div className="min-h-full">
      {/* Modals */}
      {detailsModal.isOpen && (
        <ResourceDetailsModal
          isOpen={detailsModal.isOpen}
          onClose={() => setDetailsModal({ isOpen: false, resourceType: null, resourceId: '' })}
          resourceType={detailsModal.resourceType!}
          resourceId={detailsModal.resourceId}
          apiUrl={apiUrl}
          region="us-east-1"
        />
      )}

      {deleteModal.isOpen && (
        <DeleteConfirmationModal
          isOpen={deleteModal.isOpen}
          onClose={() =>
            setDeleteModal(prev => ({ ...prev, isOpen: false }))
          }
          onConfirm={handleConfirmDelete}
          resourceType={deleteModal.resourceType!}
          resourceId={deleteModal.resourceId}
          resourceName={deleteModal.resourceName}
          showForceOption={deleteModal.showForceOption}
        />
      )}

      {/* Notification Center */}
      <NotificationCenter notifications={notifications} onDismiss={dismissNotification} />

      {/* Header */}
      <DashboardHeader selectedRegions={selectedRegions} />

      {/* Main Content */}
      <main className="px-6 py-8 space-y-8">
        {selectedService ? (
          <ServiceResourceView
            service={selectedService}
            onBack={handleBackToServices}
            onViewDetails={handleViewDetails}
            onDelete={handleDelete}
          />
        ) : (
          <>
             {/* Stats Row */}
            <DashboardStats 
                summary={summary} 
                loading={summaryLoading} 
                serviceCount={services.length} 
                servicesLoading={servicesLoading} 
            />

            {/* Controls Row */}
            <div className="grid gap-6">
                <div className="">
                    <ScanControl 
                      onScanComplete={handleScanComplete}
                      selectedRegions={selectedRegions}
                      onRegionChange={setSelectedRegions}
                    />
                </div>
                <div className="">
                    <ScheduleSettings />
                </div>
            </div>

            {/* Services Grid */}
            <div className="space-y-4">
                 <div className="flex items-center justify-between">
                    <div>
                         <h2 className="text-lg font-semibold text-slate-900">Discovered Services</h2>
                         <p className="text-sm text-slate-500">
                           Services with identified resources in your AWS environment.
                         </p>
                    </div>
                 </div>
                 <ServiceGrid
                    services={services}
                    loading={servicesLoading}
                    error={servicesError}
                    onServiceClick={handleServiceClick}
                  />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
