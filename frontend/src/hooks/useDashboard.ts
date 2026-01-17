import { useState } from 'react';
import { useServices } from '@/hooks/useServices';
import { useResourceSummary } from '@/hooks/useResourcesV2';
import { useNotifications } from '@/hooks/useNotifications';
import { Service, Resource, ResourceType } from '@/lib/api/types';

export function useDashboard() {
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  
  // Modals State
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

  // Data Hooks
  const { services, loading: servicesLoading, error: servicesError, refetch: refetchServices } = useServices();
  const { summary, loading: summaryLoading, refetch: refetchSummary } = useResourceSummary();
  const { notifications, addNotification, dismissNotification } = useNotifications();

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

  // Handlers
  const handleServiceClick = (service: Service) => {
    setSelectedService(service);
  };

  const handleBackToServices = () => {
    setSelectedService(null);
    refetchServices();
  };

  const mapResourceType = (type: string): ResourceType | null => {
    if (!type) return null;
    const lowered = type.toLowerCase();
    
    // Explicit mappings
    if (type === 'AWS::EC2::Instance' || type === 'EC2Instance') return 'ec2';
    if (type === 'AWS::EC2::Volume' || type === 'EBSVolume') return 'ebs';
    if (type === 'AWS::S3::Bucket' || type === 'S3Bucket') return 's3';
    if (type === 'AWS::IAM::Role' || type === 'IAMRole') return 'iam-role';
    if (type === 'AWS::IAM::User' || type === 'IAMUser') return 'iam-user';
    
    // Generic check
    const validTypes: ResourceType[] = ['ec2', 'ebs', 's3', 'iam-role', 'iam-user'];
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
      setDeleteModal(prev => ({ ...prev, isOpen: false }));
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: error instanceof Error ? error.message : 'Failed to delete resource',
        duration: 6000,
      });
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

  return {
    // State
    selectedService,
    selectedRegions,
    setSelectedRegions,
    detailsModal,
    setDetailsModal,
    deleteModal,
    setDeleteModal,
    notifications,
    
    // Data
    services,
    servicesLoading,
    servicesError,
    summary,
    summaryLoading,
    apiUrl,

    // Actions
    handleServiceClick,
    handleBackToServices,
    handleViewDetails,
    handleDelete,
    handleConfirmDelete,
    handleScanComplete,
    dismissNotification
  };
}
