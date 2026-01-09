'use client';

import { useState } from 'react';
import { useServices } from '@/hooks/useServices';
import { useResourceSummary } from '@/hooks/useResourcesV2';
import { Service } from '@/lib/api/types';
import ScanControl from '@/components/v2/ScanControl';
import ServiceGrid from '@/components/v2/ServiceGrid';
import ServiceResourceView from '@/components/v2/ServiceResourceView';
import StatCard from '@/components/StatCard';
import NotificationCenter from '@/components/NotificationCenter';
import ResourceDetailsModal from '@/components/ResourceDetailsModal';
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal';
import ScheduleSettings from '@/components/ScheduleSettings';
import { useNotifications } from '@/hooks/useNotifications';

export default function DashboardV2() {
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [detailsModal, setDetailsModal] = useState<{
    isOpen: boolean;
    resourceType: any;
    resourceId: string;
  }>({ isOpen: false, resourceType: null, resourceId: '' });
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    resourceType: any;
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

  const mapResourceType = (type: string): any => {
    if (!type) return null;
    if (type === 'AWS::EC2::Instance' || type === 'EC2Instance') return 'ec2';
    if (type === 'AWS::EC2::Volume' || type === 'EBSVolume') return 'ebs';
    if (type === 'AWS::S3::Bucket' || type === 'S3Bucket') return 's3';
    if (type === 'AWS::IAM::Role' || type === 'IAMRole') return 'iam-role';
    if (type === 'AWS::IAM::User' || type === 'IAMUser') return 'iam-user';
    return type.toLowerCase();
  };

  const handleViewDetails = (resource: any) => {
    setDetailsModal({
      isOpen: true,
      resourceType: mapResourceType(resource.resource_type),
      resourceId: resource.resource_id,
    });
  };

  const handleDelete = (resource: any) => {
    setDeleteModal({
      isOpen: true,
      resourceType: resource.resource_type,
      resourceId: resource.id,
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Modals */}
      {detailsModal.isOpen && (
        <ResourceDetailsModal
          isOpen={detailsModal.isOpen}
          onClose={() => setDetailsModal({ isOpen: false, resourceType: null, resourceId: '' })}
          resourceType={detailsModal.resourceType}
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
          resourceType={deleteModal.resourceType}
          resourceId={deleteModal.resourceId}
          resourceName={deleteModal.resourceName}
          showForceOption={deleteModal.showForceOption}
        />
      )}

      {/* Notification Center */}
      <NotificationCenter notifications={notifications} onDismiss={dismissNotification} />

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/50 shadow-lg sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-2xl">☁️</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Cloud Cleaner Dashboard
                </h1>
                <p className="mt-1 text-sm text-slate-600">
                  Dynamic AWS Resource Discovery v0.5.0
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                v0.5.0
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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
            {/* Scan Control */}
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
              <ScanControl onScanComplete={handleScanComplete} />
            </div>

            {/* Overall Statistics */}
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <StatCard
                  title="Total Resources"
                  value={summary?.total_resources || 0}
                  icon="📦"
                  bgColor="bg-gradient-to-br from-blue-500 to-blue-600"
                  loading={summaryLoading}
                />
                <StatCard
                  title="Unused Resources"
                  value={summary?.unused_resources || 0}
                  icon="⚠️"
                  bgColor="bg-gradient-to-br from-red-500 to-red-600"
                  loading={summaryLoading}
                />
                <StatCard
                  title="Services Discovered"
                  value={services.length}
                  icon="🔍"
                  bgColor="bg-gradient-to-br from-purple-500 to-purple-600"
                  loading={servicesLoading}
                />
              </div>
            </div>

            {/* Schedule Settings */}
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-600">
              <ScheduleSettings />
            </div>

            {/* Services Grid */}
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">Discovered Services</h2>
                <p className="text-sm text-slate-600">
                  Click on a service to view its resources and identify unused ones
                </p>
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
