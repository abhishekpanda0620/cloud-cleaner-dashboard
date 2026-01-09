'use client';

import { useState } from 'react';
import { useServices } from '@/hooks/useServices';
import { useResourceSummary } from '@/hooks/useResourcesV2';
import { Service, Resource, ResourceType } from '@/lib/api/types';
import ScanControl from '@/components/v2/ScanControl';
import ServiceGrid from '@/components/v2/ServiceGrid';
import ServiceResourceView from '@/components/v2/ServiceResourceView';
import StatCard from '@/components/StatCard';
import NotificationCenter from '@/components/NotificationCenter';
import ResourceDetailsModal from '@/components/ResourceDetailsModal';
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal';
import ScheduleSettings from '@/components/ScheduleSettings';
import { useNotifications } from '@/hooks/useNotifications';
import { Package, AlertTriangle, Search, LayoutGrid } from 'lucide-react';

export default function DashboardV2() {
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [detailsModal, setDetailsModal] = useState<{
    isOpen: boolean;
    resourceType: ResourceType | null;
    resourceId: string;
  }>({ isOpen: false, resourceType: null, resourceId: '' });
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    resourceType: ResourceType | null;
    resourceId: string;
    resourceName: string;
    showForceOption: boolean;
  }>({ isOpen: false, resourceType: null, resourceId: '', resourceName: '', showForceOption: false });

  const { services, loading: servicesLoading, error: servicesError, refetch: refetchServices } = useServices();
  const { summary, loading: summaryLoading, refetch: refetchSummary } = useResourceSummary();
  const { notifications, addNotification, dismissNotification } = useNotifications();

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

  const handleServiceClick = (service: Service) => {
    setSelectedService(service);
  };

  const handleBackToServices = () => {
    setSelectedService(null);
    refetchServices();
  };

  const mapResourceType = (type: string): ResourceType | null => {
    if (!type) return null;
    if (type === 'AWS::EC2::Instance' || type === 'EC2Instance') return 'ec2';
    if (type === 'AWS::EC2::Volume' || type === 'EBSVolume') return 'ebs';
    if (type === 'AWS::S3::Bucket' || type === 'S3Bucket') return 's3';
    if (type === 'AWS::IAM::Role' || type === 'IAMRole') return 'iam-role';
    if (type === 'AWS::IAM::User' || type === 'IAMUser') return 'iam-user';
    
    // Check if the type matches one of the valid ResourceType values
    const validTypes: ResourceType[] = ['ec2', 'ebs', 's3', 'iam-role', 'iam-user'];
    const lowered = type.toLowerCase();
    if (validTypes.includes(lowered as ResourceType)) {
      return lowered as ResourceType;
    }
    
    return null;
  };

  const handleViewDetails = (resource: Resource) => {
    setDetailsModal({
      isOpen: true,
      resourceType: mapResourceType(resource.resource_type),
      resourceId: resource.resource_id,
    });
  };

  const handleDelete = (resource: Resource) => {
    setDeleteModal({
      isOpen: true,
      resourceType: mapResourceType(resource.resource_type),
      resourceId: resource.resource_id,
      resourceName: resource.resource_name || resource.resource_id,
      showForceOption: false,
    });
  };

  const handleConfirmDelete = async () => {
    try {
      const response = await fetch(`${apiUrl}/v2/resources/${deleteModal.resourceId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete resource');
      }

      addNotification({
        type: 'success',
        title: 'Resource Deleted',
        message: `Successfully deleted ${deleteModal.resourceName}`,
        duration: 5000,
      });

      // Refresh data
      refetchServices();
      refetchSummary();
      if (selectedService) {
        setSelectedService(null);
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: error instanceof Error ? error.message : 'Failed to delete resource',
        duration: 6000,
      });
      throw error;
    }
  };

  const handleScanComplete = () => {
    refetchServices();
    refetchSummary();
    addNotification({
      type: 'success',
      title: 'Scan Complete',
      message: 'Dashboard updated with latest findings',
      duration: 4000
    });
  };

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
            setDeleteModal({
              isOpen: false,
              resourceType: null,
              resourceId: '',
              resourceName: '',
              showForceOption: false,
            })
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
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 py-4">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-slate-100 p-2 rounded-lg border border-slate-200">
                <LayoutGrid className="w-5 h-5 text-slate-900" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900 leading-tight">
                  Resource Dashboard
                </h1>
                <p className="text-sm text-slate-500">
                  Dynamic AWS Discovery
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 text-xs font-medium bg-slate-100 text-slate-600 rounded border border-slate-200">
                us-east-1
              </span>
            </div>
          </div>
      </header>

      {/* Main Content */}
      <main className="px-6 py-8 space-y-8">
        {selectedService ? (
          /* Service Detail View */
          <ServiceResourceView
            service={selectedService}
            onBack={handleBackToServices}
            onViewDetails={handleViewDetails}
            onDelete={handleDelete}
          />
        ) : (
          /* Services Overview */
          <>
             {/* Stats Row (Full Width) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatCard
                    title="Total Resources"
                    value={summary?.total_resources || 0}
                    icon={<Package className="w-5 h-5" />}
                    loading={summaryLoading}
                    iconClassName="text-blue-500"
                    iconBgClassName="bg-blue-50"
                />
                <StatCard
                    title="Unused Resources"
                    value={summary?.unused_resources || 0}
                    icon={<AlertTriangle className="w-5 h-5" />}
                    loading={summaryLoading}
                    iconClassName="text-amber-500"
                    iconBgClassName="bg-amber-50"
                />
                <StatCard
                    title="Services"
                    value={services.length}
                    icon={<Search className="w-5 h-5" />}
                    loading={servicesLoading}
                    iconClassName="text-purple-500"
                    iconBgClassName="bg-purple-50"
                />
            </div>

            {/* Controls Row (Full Width - 2 columns) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Scan Control (1/3) */}
                <div className="lg:col-span-1">
                    <ScanControl onScanComplete={handleScanComplete} />
                </div>
                {/* Schedule Settings (2/3) - WIDER as requested */}
                <div className="lg:col-span-2">
                    <ScheduleSettings />
                </div>
            </div>

            {/* Services Grid (Full Width) */}
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
