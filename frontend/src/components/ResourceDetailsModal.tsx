"use client";

import { useEffect, useState } from 'react';

interface ResourceDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  resourceType: 'ec2' | 'ebs' | 's3' | 'iam-role' | 'iam-user';
  resourceId: string;
  apiUrl: string;
}

export default function ResourceDetailsModal({
  isOpen,
  onClose,
  resourceType,
  resourceId,
  apiUrl
}: ResourceDetailsModalProps) {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && resourceId) {
      fetchDetails();
    }
  }, [isOpen, resourceId]);

  const fetchDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      let endpoint = '';
      switch (resourceType) {
        case 'ec2':
          endpoint = `${apiUrl}/ec2/${resourceId}`;
          break;
        case 'ebs':
          endpoint = `${apiUrl}/ebs/${resourceId}`;
          break;
        case 's3':
          endpoint = `${apiUrl}/s3/${resourceId}`;
          break;
        case 'iam-role':
          endpoint = `${apiUrl}/iam/roles/${resourceId}`;
          break;
        case 'iam-user':
          endpoint = `${apiUrl}/iam/users/${resourceId}`;
          break;
      }

      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`Failed to fetch details: ${response.statusText}`);
      }

      const data = await response.json();
      setDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch details');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const renderDetailValue = (value: any): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  const renderEC2Details = () => (
    <div className="space-y-4">
      <DetailRow label="Instance ID" value={details.id} />
      <DetailRow label="Name" value={details.name} />
      <DetailRow label="Type" value={details.type} />
      <DetailRow label="State" value={details.state} badge />
      <DetailRow label="Launch Time" value={details.launch_time} />
      <DetailRow label="Availability Zone" value={details.availability_zone} />
      <DetailRow label="VPC ID" value={details.vpc_id} />
      <DetailRow label="Subnet ID" value={details.subnet_id} />
      <DetailRow label="Private IP" value={details.private_ip} />
      <DetailRow label="Public IP" value={details.public_ip} />
      <DetailRow label="Key Name" value={details.key_name} />
      <DetailRow label="Platform" value={details.platform} />
      <DetailRow label="Architecture" value={details.architecture} />
      <DetailRow label="Monitoring" value={details.monitoring} />
      
      {details.security_groups && details.security_groups.length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Security Groups</h4>
          <div className="space-y-1">
            {details.security_groups.map((sg: any, idx: number) => (
              <div key={idx} className="text-sm text-gray-600">
                {sg.name} ({sg.id})
              </div>
            ))}
          </div>
        </div>
      )}
      
      {details.tags && Object.keys(details.tags).length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Tags</h4>
          <div className="space-y-1">
            {Object.entries(details.tags).map(([key, value]) => (
              <div key={key} className="text-sm text-gray-600">
                <span className="font-medium">{key}:</span> {String(value)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderEBSDetails = () => (
    <div className="space-y-4">
      <DetailRow label="Volume ID" value={details.id} />
      <DetailRow label="Name" value={details.name} />
      <DetailRow label="Size" value={`${details.size} GB`} />
      <DetailRow label="Type" value={details.type} />
      <DetailRow label="State" value={details.state} badge />
      <DetailRow label="Created" value={details.create_time} />
      <DetailRow label="Availability Zone" value={details.availability_zone} />
      <DetailRow label="Encrypted" value={details.encrypted} />
      <DetailRow label="IOPS" value={details.iops} />
      <DetailRow label="Throughput" value={details.throughput} />
      
      {details.attachments && details.attachments.length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Attachments</h4>
          <div className="space-y-2">
            {details.attachments.map((att: any, idx: number) => (
              <div key={idx} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                <div>Instance: {att.instance_id}</div>
                <div>Device: {att.device}</div>
                <div>State: {att.state}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderS3Details = () => (
    <div className="space-y-4">
      <DetailRow label="Bucket Name" value={details.name} />
      <DetailRow label="Region" value={details.location} />
      <DetailRow label="Created" value={details.creation_date} />
      <DetailRow label="Object Count" value={details.object_count} />
      <DetailRow label="Total Size" value={`${details.total_size_mb} MB`} />
      <DetailRow label="Versioning" value={details.versioning_status} badge />
      <DetailRow label="Encryption" value={details.encryption_enabled ? 'Enabled' : 'Disabled'} badge />
      <DetailRow label="Encryption Type" value={details.encryption_type} />
      <DetailRow label="Is Empty" value={details.is_empty} />
      
      {details.tags && Object.keys(details.tags).length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Tags</h4>
          <div className="space-y-1">
            {Object.entries(details.tags).map(([key, value]) => (
              <div key={key} className="text-sm text-gray-600">
                <span className="font-medium">{key}:</span> {String(value)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderIAMRoleDetails = () => (
    <div className="space-y-4">
      <DetailRow label="Role Name" value={details.name} />
      <DetailRow label="ARN" value={details.arn} />
      <DetailRow label="Created" value={details.create_date} />
      <DetailRow label="Last Used" value={details.last_used_date || 'Never'} />
      <DetailRow label="Last Used Region" value={details.last_used_region} />
      <DetailRow label="Description" value={details.description} />
      <DetailRow label="Max Session Duration" value={`${details.max_session_duration} seconds`} />
      
      {details.attached_policies && details.attached_policies.length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Attached Policies</h4>
          <div className="space-y-1">
            {details.attached_policies.map((policy: any, idx: number) => (
              <div key={idx} className="text-sm text-gray-600">
                {policy.name}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {details.inline_policies && details.inline_policies.length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Inline Policies</h4>
          <div className="space-y-1">
            {details.inline_policies.map((policy: string, idx: number) => (
              <div key={idx} className="text-sm text-gray-600">
                {policy}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderIAMUserDetails = () => (
    <div className="space-y-4">
      <DetailRow label="User Name" value={details.name} />
      <DetailRow label="ARN" value={details.arn} />
      <DetailRow label="Created" value={details.create_date} />
      <DetailRow label="Password Last Used" value={details.password_last_used || 'Never'} />
      <DetailRow label="Console Access" value={details.has_console_access} />
      
      {details.access_keys && details.access_keys.length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Access Keys</h4>
          <div className="space-y-2">
            {details.access_keys.map((key: any, idx: number) => (
              <div key={idx} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                <div>Key ID: {key.access_key_id}</div>
                <div>Status: <span className={key.status === 'Active' ? 'text-green-600' : 'text-red-600'}>{key.status}</span></div>
                <div>Created: {key.create_date}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {details.groups && details.groups.length > 0 && (
        <div className="pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">Groups</h4>
          <div className="space-y-1">
            {details.groups.map((group: string, idx: number) => (
              <div key={idx} className="text-sm text-gray-600">
                {group}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 z-[9999] overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay with blur */}
        <div
          className="fixed inset-0 transition-opacity backdrop-blur-sm bg-black/20"
          onClick={onClose}
        />

        {/* Center alignment helper */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full relative z-10">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">
                Resource Details
              </h3>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                <p className="font-semibold">Error loading details</p>
                <p className="text-sm">{error}</p>
              </div>
            )}

            {!loading && !error && details && (
              <>
                {resourceType === 'ec2' && renderEC2Details()}
                {resourceType === 'ebs' && renderEBSDetails()}
                {resourceType === 's3' && renderS3Details()}
                {resourceType === 'iam-role' && renderIAMRoleDetails()}
                {resourceType === 'iam-user' && renderIAMUserDetails()}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function DetailRow({ label, value, badge = false }: { label: string; value: any; badge?: boolean }) {
  const displayValue = value === null || value === undefined ? 'N/A' : String(value);
  
  return (
    <div className="flex justify-between items-start py-2 border-b border-gray-100">
      <span className="text-sm font-medium text-gray-600">{label}</span>
      {badge ? (
        <span className={`px-2 py-1 text-xs rounded-full ${
          displayValue.toLowerCase().includes('running') || displayValue.toLowerCase().includes('active') || displayValue.toLowerCase().includes('enabled')
            ? 'bg-green-100 text-green-800'
            : displayValue.toLowerCase().includes('stopped') || displayValue.toLowerCase().includes('disabled')
            ? 'bg-yellow-100 text-yellow-800'
            : 'bg-gray-100 text-gray-800'
        }`}>
          {displayValue}
        </span>
      ) : (
        <span className="text-sm text-gray-900 text-right max-w-md break-words">{displayValue}</span>
      )}
    </div>
  );
}