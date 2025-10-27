"use client"
import { useEffect, useState } from "react";
import ResourceTab from "@/components/ResourceTab";
import NotificationCenter from "@/components/NotificationCenter";
import AlertPanel from "@/components/AlertPanel";
import ScheduleSettings from "@/components/ScheduleSettings";
import ResourceDetailsModal from "@/components/ResourceDetailsModal";
import DeleteConfirmationModal from "@/components/DeleteConfirmationModal";
import RegionSelector from "@/components/RegionSelector";
import { useNotifications } from "@/hooks/useNotifications";

interface EC2Instance {
  id: string;
  state: string;
}

interface EBSVolume {
  id: string;
  size: number;
  state: string;
}

interface S3Bucket {
  name: string;
  creation_date: string;
}

interface IAMRole {
  name: string;
  last_used_date?: string;
  create_date?: string;
}

interface IAMUser {
  name: string;
  create_date: string;
  arn: string;
  has_console_access: boolean;
  access_keys_count: number;
  access_keys: Array<{
    access_key_id: string;
    status: string;
    create_date: string;
  }>;
}

interface AccessKey {
  access_key_id: string;
  user_name: string;
  status: string;
  create_date: string;
  last_used_date?: string;
  security_risk: string;
}

interface DashboardData {
  ec2: EC2Instance[];
  ebs: EBSVolume[];
  s3: S3Bucket[];
  iam: IAMRole[];
  iam_users: IAMUser[];
  access_keys: AccessKey[];
}

type TabType = 'ec2' | 'ebs' | 's3' | 'iam' | 'iam_users' | 'access_keys';

export default function Dashboard() {
  const [data, setData] = useState<DashboardData>({
    ec2: [],
    ebs: [],
    s3: [],
    iam: [],
    iam_users: [],
    access_keys: []
  });
  const [loading, setLoading] = useState(true);
  const [loadingStates, setLoadingStates] = useState<Record<TabType, boolean>>({
    ec2: true,
    ebs: true,
    s3: true,
    iam: true,
    iam_users: true,
    access_keys: true
  });
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('ec2');
  const [selectedRegion, setSelectedRegion] = useState<string>('us-east-1'); // Default region
  const [detailsModal, setDetailsModal] = useState<{
    isOpen: boolean;
    resourceType: 'ec2' | 'ebs' | 's3' | 'iam-role' | 'iam-user' | null;
    resourceId: string;
  }>({ isOpen: false, resourceType: null, resourceId: '' });
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    resourceType: 'ec2' | 'ebs' | 's3' | 'iam-role' | 'iam-user' | null;
    resourceId: string;
    resourceName: string;
    showForceOption: boolean;
  }>({ isOpen: false, resourceType: null, resourceId: '', resourceName: '', showForceOption: false });
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8084/api";
  const { notifications, addNotification, dismissNotification } = useNotifications();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Reset all loading states to true
        setLoadingStates({
          ec2: true,
          ebs: true,
          s3: true,
          iam: true,
          iam_users: true,
          access_keys: true
        });
        
        // Add region parameter for regional resources (EC2, EBS)
        const regionParam = selectedRegion ? `?region=${selectedRegion}` : '';
        
        const endpoints = [
          { url: `${apiUrl}/ec2/unused${regionParam}`, key: 'ec2' as TabType, dataKey: 'unused_instances' },
          { url: `${apiUrl}/ebs/unused${regionParam}`, key: 'ebs' as TabType, dataKey: 'unused_volumes' },
          { url: `${apiUrl}/s3/unused`, key: 's3' as TabType, dataKey: 'unused_buckets' },
          { url: `${apiUrl}/iam/unused`, key: 'iam' as TabType, dataKey: 'unused_roles' },
          { url: `${apiUrl}/iam/users/unused`, key: 'iam_users' as TabType, dataKey: 'unused_users' },
          { url: `${apiUrl}/iam/access-keys/unused`, key: 'access_keys' as TabType, dataKey: 'unused_keys' }
        ];

        const errors: string[] = [];
        let loadedCount = 0;

        // Fetch resources one by one (lazy loading)
        for (const endpoint of endpoints) {
          try {
            const response = await fetch(endpoint.url);
            
            if (response.ok) {
              const jsonData = await response.json();
              const resourceData = jsonData[endpoint.dataKey] || [];
              
              // Update state immediately as each resource loads
              setData(prevData => ({
                ...prevData,
                [endpoint.key]: resourceData
              }));
              
              // Mark this resource as loaded
              setLoadingStates(prev => ({
                ...prev,
                [endpoint.key]: false
              }));
              
              loadedCount++;
              
              // Turn off global loading after first resource loads
              if (loadedCount === 1) {
                setLoading(false);
                addNotification({
                  type: 'info',
                  title: 'Loading Resources',
                  message: `Loading AWS resources... (${loadedCount}/${endpoints.length})`,
                  duration: 2000
                });
              }
            } else {
              errors.push(`${endpoint.key}: ${response.status} ${response.statusText}`);
              console.error(`Error fetching ${endpoint.key}:`, response.statusText);
              // Mark as not loading even on error
              setLoadingStates(prev => ({
                ...prev,
                [endpoint.key]: false
              }));
            }
          } catch (err) {
            errors.push(`${endpoint.key}: ${err instanceof Error ? err.message : 'Network error'}`);
            console.error(`Error fetching ${endpoint.key}:`, err);
            // Mark as not loading even on error
            setLoadingStates(prev => ({
              ...prev,
              [endpoint.key]: false
            }));
          }
        }

        // Show final notification and set connection status
        if (errors.length > 0) {
          setError(`Some resources failed to load: ${errors.join(', ')}`);
          setIsConnected(loadedCount > 0); // Connected if at least one resource loaded
          addNotification({
            type: 'warning',
            title: 'Partial Data Load',
            message: `Loaded ${loadedCount}/${endpoints.length} resource types. ${errors.length} failed.`,
            duration: 6000
          });
        } else {
          setIsConnected(true); // All resources loaded successfully
          const totalResources = Object.values(data).reduce((sum, arr) => sum + arr.length, 0);
          addNotification({
            type: 'success',
            title: 'All Resources Loaded',
            message: `Successfully loaded all ${endpoints.length} resource types${totalResources > 0 ? ` (${totalResources} unused resources found)` : ''}`,
            duration: 4000
          });
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Failed to fetch data";
        setError(errorMsg);
        setIsConnected(false); // Not connected on complete failure
        addNotification({
          type: 'error',
          title: 'Failed to Load Resources',
          message: errorMsg,
          duration: 6000
        });
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [apiUrl, addNotification, selectedRegion]);

  const handleRegionChange = (region: string) => {
    setSelectedRegion(region);
    addNotification({
      type: 'info',
      title: 'Region Changed',
      message: `Switching to ${region}. Reloading resources...`,
      duration: 3000
    });
  };

  const refreshData = () => {
    window.location.reload();
  };

  const handleViewDetails = (resourceType: 'ec2' | 'ebs' | 's3' | 'iam-role' | 'iam-user', row: any) => {
    const resourceId = resourceType === 's3' ? row.name : resourceType.includes('iam') ? row.name : row.id;
    setDetailsModal({
      isOpen: true,
      resourceType,
      resourceId
    });
  };

  const handleDelete = (resourceType: 'ec2' | 'ebs' | 's3' | 'iam-role' | 'iam-user', row: any, showForce: boolean = false) => {
    const resourceId = resourceType === 's3' ? row.name : resourceType.includes('iam') ? row.name : row.id;
    const resourceName = row.name || row.id;
    setDeleteModal({
      isOpen: true,
      resourceType,
      resourceId,
      resourceName,
      showForceOption: showForce
    });
  };

  const handleConfirmDelete = async (force?: boolean) => {
    if (!deleteModal.resourceType || !deleteModal.resourceId) return;

    try {
      let endpoint = '';
      let method = 'DELETE';
      
      switch (deleteModal.resourceType) {
        case 'ec2':
          endpoint = `${apiUrl}/ec2/${deleteModal.resourceId}?region=${selectedRegion}`;
          break;
        case 'ebs':
          endpoint = `${apiUrl}/ebs/${deleteModal.resourceId}?region=${selectedRegion}`;
          break;
        case 's3':
          endpoint = `${apiUrl}/s3/${deleteModal.resourceId}${force ? '?force=true' : ''}`;
          break;
        case 'iam-role':
          endpoint = `${apiUrl}/iam/roles/${deleteModal.resourceId}${force ? '?force=true' : ''}`;
          break;
        case 'iam-user':
          endpoint = `${apiUrl}/iam/users/${deleteModal.resourceId}${force ? '?force=true' : ''}`;
          break;
      }

      const response = await fetch(endpoint, { method });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Failed to delete resource: ${response.statusText}`);
      }

      const result = await response.json();

      addNotification({
        type: 'success',
        title: 'Resource Deleted',
        message: result.message || `Successfully deleted ${deleteModal.resourceType} ${deleteModal.resourceName}`,
        duration: 5000
      });

      // Refresh data after successful deletion
      setTimeout(refreshData, 1000);
      
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: error instanceof Error ? error.message : 'Failed to delete resource',
        duration: 6000
      });
      throw error;
    }
  };

  const tabs = [
    { id: 'ec2' as TabType, label: '🖥️ EC2 Instances', count: data.ec2.length, color: 'blue' },
    { id: 'ebs' as TabType, label: '💾 EBS Volumes', count: data.ebs.length, color: 'purple' },
    { id: 's3' as TabType, label: '🪣 S3 Buckets', count: data.s3.length, color: 'orange' },
    { id: 'iam' as TabType, label: '🔐 IAM Roles', count: data.iam.length, color: 'green' },
    { id: 'iam_users' as TabType, label: '👥 IAM Users', count: data.iam_users.length, color: 'indigo' },
    { id: 'access_keys' as TabType, label: '🔑 Access Keys', count: data.access_keys.length, color: 'red' }
  ];

  const ec2Columns = [
    { header: 'Instance ID', accessor: 'id', render: (value: string) => <span className="font-mono text-sm font-medium text-slate-900">{value}</span> },
    {
      header: 'State',
      accessor: 'state',
      render: (value: string) => (
        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
          {value}
        </span>
      )
    }
  ];

  const ebsColumns = [
    { header: 'Volume ID', accessor: 'id', render: (value: string) => <span className="font-mono text-sm font-medium text-slate-900">{value}</span> },
    { header: 'Size', accessor: 'size', render: (value: number) => <span className="text-sm font-semibold text-slate-900">{value} GB</span> },
    {
      header: 'State',
      accessor: 'state',
      render: (value: string) => (
        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
          {value}
        </span>
      )
    }
  ];

  const s3Columns = [
    { header: 'Bucket Name', accessor: 'name', render: (value: string) => <span className="font-mono text-sm font-medium text-slate-900">{value}</span> },
    {
      header: 'Created',
      accessor: 'creation_date',
      render: (value: string) => <span className="text-sm text-slate-600">{new Date(value).toLocaleDateString()}</span>
    }
  ];

  const iamColumns = [
    { header: 'Role Name', accessor: 'name', render: (value: string) => <span className="font-mono text-sm font-medium text-slate-900">{value}</span> },
    {
      header: 'Last Used',
      accessor: 'last_used_date',
      render: (value: string) => <span className="text-sm text-slate-600">{value ? new Date(value).toLocaleDateString() : 'Never'}</span>
    }
  ];

  const iamUsersColumns = [
    { header: 'User Name', accessor: 'name', render: (value: string) => <span className="font-mono text-sm font-medium text-slate-900">{value}</span> },
    {
      header: 'Console Access',
      accessor: 'has_console_access',
      render: (value: boolean) => (
        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
          {value ? '✓ Yes' : '✗ No'}
        </span>
      )
    },
    {
      header: 'Access Keys',
      accessor: 'access_keys_count',
      render: (value: number) => <span className="text-sm font-semibold text-slate-900">{value}</span>
    },
    {
      header: 'Created',
      accessor: 'create_date',
      render: (value: string) => <span className="text-sm text-slate-600">{new Date(value).toLocaleDateString()}</span>
    }
  ];

  const accessKeysColumns = [
    { header: 'Access Key ID', accessor: 'access_key_id', render: (value: string) => <span className="font-mono text-xs font-medium text-slate-900">{value.substring(0, 10)}...</span> },
    { header: 'User Name', accessor: 'user_name', render: (value: string) => <span className="text-sm font-medium text-slate-900">{value}</span> },
    {
      header: 'Status',
      accessor: 'status',
      render: (value: string) => (
        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${value === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
          {value}
        </span>
      )
    },
    {
      header: 'Last Used',
      accessor: 'last_used_date',
      render: (value: string) => <span className="text-sm text-slate-600">{value ? new Date(value).toLocaleDateString() : 'Never'}</span>
    },
    {
      header: 'Security Risk',
      accessor: 'security_risk',
      render: (value: string) => (
        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${value === 'High' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
          {value}
        </span>
      )
    }
  ];

  const resourceConfig = {
    ec2: {
      columns: ec2Columns,
      data: data.ec2,
      icon: '🖥️',
      emptyTitle: 'No stopped EC2 instances',
      emptyDescription: 'All your instances are running efficiently!',
      infoNote: 'These EC2 instances have been stopped for more than 7 days and were stopped by a user. Stopped instances still incur EBS storage costs. Consider terminating them if no longer needed.',
      onViewDetails: (row: any) => handleViewDetails('ec2', row),
      onDelete: (row: any) => handleDelete('ec2', row, false),
      searchFields: ['id', 'state'],
      filterConfigs: [
        {
          name: 'state',
          label: 'State',
          options: [
            { label: 'Stopped', value: 'stopped' },
            { label: 'Stopping', value: 'stopping' },
          ],
          filterFn: (item: any, value: string) => item.state === value,
        },
      ],
    },
    ebs: {
      columns: ebsColumns,
      data: data.ebs,
      icon: '💾',
      emptyTitle: 'No unattached EBS volumes',
      emptyDescription: 'All your volumes are properly attached!',
      infoNote: 'These EBS volumes are not attached to any EC2 instance and are in "available" state. Unattached volumes still incur storage costs. Delete them if the data is no longer needed.',
      onViewDetails: (row: any) => handleViewDetails('ebs', row),
      onDelete: (row: any) => handleDelete('ebs', row, false),
      searchFields: ['id', 'state'],
      filterConfigs: [
        {
          name: 'size',
          label: 'Size',
          options: [
            { label: 'Small (< 50 GB)', value: 'small' },
            { label: 'Medium (50-200 GB)', value: 'medium' },
            { label: 'Large (> 200 GB)', value: 'large' },
          ],
          filterFn: (item: any, value: string) => {
            if (value === 'small') return item.size < 50;
            if (value === 'medium') return item.size >= 50 && item.size <= 200;
            if (value === 'large') return item.size > 200;
            return true;
          },
        },
        {
          name: 'state',
          label: 'State',
          options: [
            { label: 'Available', value: 'available' },
            { label: 'Creating', value: 'creating' },
          ],
          filterFn: (item: any, value: string) => item.state === value,
        },
      ],
    },
    s3: {
      columns: s3Columns,
      data: data.s3,
      icon: '🪣',
      emptyTitle: 'No unused S3 buckets',
      emptyDescription: 'All your buckets are being used!',
      infoNote: 'These S3 buckets are either empty or haven\'t been accessed in 90+ days. Empty buckets have minimal cost, but old buckets may contain forgotten data incurring storage charges.',
      onViewDetails: (row: any) => handleViewDetails('s3', row),
      onDelete: (row: any) => handleDelete('s3', row, true),
      searchFields: ['name'],
      filterConfigs: [],
      
    },
    iam: {
      columns: iamColumns,
      data: data.iam,
      icon: '🔐',
      emptyTitle: 'No unused IAM roles',
      emptyDescription: 'All your roles are actively being used!',
      infoNote: 'These IAM roles haven\'t been used in 90+ days or have never been used. Unused roles pose a security risk and should be deleted to follow the principle of least privilege.',
      onViewDetails: (row: any) => handleViewDetails('iam-role', row),
      onDelete: (row: any) => handleDelete('iam-role', row, true),
      searchFields: ['name'],
      filterConfigs: [
        {
          name: 'usage',
          label: 'Usage',
          options: [
            { label: 'Never Used', value: 'never' },
            { label: 'Not Recently Used', value: 'old' },
          ],
          filterFn: (item: any, value: string) => {
            if (value === 'never') return !item.last_used_date;
            if (value === 'old') return !!item.last_used_date;
            return true;
          },
        },
      ],
    },
    iam_users: {
      columns: iamUsersColumns,
      data: data.iam_users,
      icon: '👥',
      emptyTitle: 'No unused IAM users',
      emptyDescription: 'All your users have recent activity!',
      infoNote: 'These IAM users either have no access keys and no console access, or haven\'t been active recently. Inactive users should be removed to reduce security risks and maintain a clean IAM structure.',
      onViewDetails: (row: any) => handleViewDetails('iam-user', row),
      onDelete: (row: any) => handleDelete('iam-user', row, true),
      searchFields: ['name', 'arn'],
      filterConfigs: [
        {
          name: 'console_access',
          label: 'Console Access',
          options: [
            { label: 'Has Access', value: 'yes' },
            { label: 'No Access', value: 'no' },
          ],
          filterFn: (item: any, value: string) => {
            if (value === 'yes') return item.has_console_access;
            if (value === 'no') return !item.has_console_access;
            return true;
          },
        },
        {
          name: 'access_keys',
          label: 'Access Keys',
          options: [
            { label: 'Has Keys', value: 'yes' },
            { label: 'No Keys', value: 'no' },
          ],
          filterFn: (item: any, value: string) => {
            if (value === 'yes') return item.access_keys_count > 0;
            if (value === 'no') return item.access_keys_count === 0;
            return true;
          },
        },
      ],
    },
    access_keys: {
      columns: accessKeysColumns,
      data: data.access_keys,
      icon: '🔑',
      emptyTitle: 'No unused access keys',
      emptyDescription: 'All your access keys are being used regularly!',
      infoNote: 'These access keys haven\'t been used in 90+ days or have never been used. Unused access keys, especially active ones, pose a significant security risk and should be deactivated or deleted immediately.',
      searchFields: ['access_key_id', 'user_name'],
      filterConfigs: [
        {
          name: 'status',
          label: 'Status',
          options: [
            { label: 'Active', value: 'Active' },
            { label: 'Inactive', value: 'Inactive' },
          ],
          filterFn: (item: any, value: string) => item.status === value,
        },
        {
          name: 'risk',
          label: 'Security Risk',
          options: [
            { label: 'High Risk', value: 'High' },
            { label: 'Medium Risk', value: 'Medium' },
          ],
          filterFn: (item: any, value: string) => item.security_risk === value,
        },
      ],
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Modals */}
      {detailsModal.isOpen && detailsModal.resourceType && (
        <ResourceDetailsModal
          isOpen={detailsModal.isOpen}
          onClose={() => setDetailsModal({ isOpen: false, resourceType: null, resourceId: '' })}
          resourceType={detailsModal.resourceType}
          resourceId={detailsModal.resourceId}
          apiUrl={apiUrl}
          region={selectedRegion}
        />
      )}

      {deleteModal.isOpen && deleteModal.resourceType && (
        <DeleteConfirmationModal
          isOpen={deleteModal.isOpen}
          onClose={() => setDeleteModal({ isOpen: false, resourceType: null, resourceId: '', resourceName: '', showForceOption: false })}
          onConfirm={handleConfirmDelete}
          resourceType={deleteModal.resourceType}
          resourceId={deleteModal.resourceId}
          resourceName={deleteModal.resourceName}
          showForceOption={deleteModal.showForceOption}
        />
      )}

      {/* Notification Center */}
      <NotificationCenter
        notifications={notifications}
        onDismiss={dismissNotification}
      />

      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                ☁️ Cloud Cleaner 🧹
              </h1>
              <p className="mt-1 text-sm text-slate-600">
                Monitor and manage your AWS resources efficiently
              </p>
            </div>
            <div className="flex items-center gap-4">
              {/* Region Selector - Only for EC2 and EBS tabs */}
              {(activeTab === 'ec2' || activeTab === 'ebs') && (
                <RegionSelector
                  selectedRegion={selectedRegion}
                  onRegionChange={handleRegionChange}
                  apiUrl={apiUrl}
                />
              )}
              <div className="flex items-center space-x-2">
                <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                <span className="text-sm text-slate-600">{isConnected ? 'Connected' : 'Not Connected'}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Alert Panel */}
        <AlertPanel
          s3Count={data.s3.length}
          iamUsersCount={data.iam_users.length}
          onAlertSent={() => {
            addNotification({
              type: 'success',
              title: 'Alert Sent',
              message: 'Resource summary has been sent to your configured channels',
              duration: 4000
            });
          }}
        />

        {/* Schedule Settings */}
        <div className="mt-6">
          <ScheduleSettings />
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="border-b border-slate-200 overflow-x-auto">
            <nav className="flex -mb-px">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? `border-${tab.color}-500 text-${tab.color}-600`
                      : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                  }`}
                >
                  {tab.label} ({tab.count})
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6 h-96 overflow-auto">
            <ResourceTab
              loading={loadingStates[activeTab]}
              error={error}
              {...resourceConfig[activeTab]}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
