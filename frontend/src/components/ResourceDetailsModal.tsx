"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */

import { useEffect, useState, useCallback } from 'react';
import { 
  X, 
  Server, 
  HardDrive, 
  Database, 
  Lock, 
  Users, 
  Key, 
  Globe, 
  Activity, 
  Tag, 
  Shield, 
  Cpu,
  Box,
  AlertTriangle
} from 'lucide-react';

import { ResourceType } from '@/lib/api/types';

interface ResourceDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  resourceType: ResourceType;
  resourceId: string;
  apiUrl: string;
  region?: string;
}

export default function ResourceDetailsModal({
  isOpen,
  onClose,
  resourceType,
  resourceId,
  apiUrl,
  region
}: ResourceDetailsModalProps) {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      let endpoint = '';
      switch (resourceType) {
        case 'ec2':
          endpoint = `${apiUrl}/ec2/${resourceId}${region ? `?region=${region}` : ''}`;
          break;
        case 'ebs':
          endpoint = `${apiUrl}/ebs/${resourceId}${region ? `?region=${region}` : ''}`;
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

      if (!endpoint) return;

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
  }, [apiUrl, region, resourceId, resourceType]);

  useEffect(() => {
    if (isOpen && resourceId) {
      fetchDetails();
    }
  }, [isOpen, resourceId, fetchDetails]);


  if (!isOpen) return null;

  const renderHeaderIcon = () => {
    switch(resourceType) {
        case 'ec2': return <Server className="w-5 h-5 text-blue-600" />;
        case 'ebs': return <HardDrive className="w-5 h-5 text-blue-600" />;
        case 's3': return <Database className="w-5 h-5 text-blue-600" />;
        case 'iam-role': return <Lock className="w-5 h-5 text-blue-600" />;
        case 'iam-user': return <Users className="w-5 h-5 text-blue-600" />;
        default: return <Box className="w-5 h-5 text-blue-600" />;
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center sm:p-4">
      <div 
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" 
        onClick={onClose}
      />

      <div className="relative w-full max-w-2xl bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden transform transition-all max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg border border-blue-100">
                {renderHeaderIcon()}
            </div>
            <div>
                <h3 className="text-lg font-semibold text-slate-900 leading-tight">Resource Details</h3>
                <p className="text-xs text-slate-500 font-mono">{resourceId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto min-h-[300px]">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-48 space-y-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-sm text-slate-500">Retrieving resource metadata...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-600 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <div>
                    <p className="font-medium">Failed to load details</p>
                    <p className="mt-1 opacity-90">{error}</p>
                </div>
            </div>
          ) : details ? (
            <div className="space-y-6">
                {/* Dynamically render content based on type */}
               {resourceType === 'ec2' && <EC2Details details={details} />}
               {resourceType === 'ebs' && <EBSDetails details={details} />}
               {resourceType === 's3' && <S3Details details={details} />}
               {resourceType === 'iam-role' && <IAMRoleDetails details={details} />}
               {resourceType === 'iam-user' && <IAMUserDetails details={details} />}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// --- Sub-components for specific resource types ---

function SectionHeader({ title, icon: Icon }: { title: string, icon: any }) {
    return (
        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2 border-b border-slate-100 pb-2">
            <Icon className="w-3.5 h-3.5" />
            {title}
        </h4>
    );
}

function DetailGrid({ children }: { children: React.ReactNode }) {
    return <div className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8">{children}</div>;
}

function DetailItem({ label, value, fullWidth = false }: { label: string, value: any, fullWidth?: boolean }) {
    if (value === null || value === undefined || value === '') return null;
    return (
        <div className={fullWidth ? "col-span-full" : ""}>
            <dt className="text-xs font-medium text-slate-500 mb-0.5">{label}</dt>
            <dd className="text-sm text-slate-900 font-medium break-words">{String(value)}</dd>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    let color = 'bg-slate-100 text-slate-700';
    if (['running', 'available', 'active', 'ok', 'enabled'].includes(status?.toLowerCase())) {
        color = 'bg-emerald-50 text-emerald-700 border border-emerald-200';
    } else if (['stopped', 'disabled', 'unused'].includes(status?.toLowerCase())) {
        color = 'bg-amber-50 text-amber-700 border border-amber-200';
    } else if (['error', 'failed'].includes(status?.toLowerCase())) {
        color = 'bg-red-50 text-red-700 border border-red-200';
    }

    return (
        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${color}`}>
            {status}
        </span>
    );
}

function EC2Details({ details }: { details: any }) {
    return (
        <>
            <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                    <dt className="text-xs font-medium text-slate-500 mb-1">State</dt>
                    <dd><StatusBadge status={details.state} /></dd>
                </div>
            </div>
            
            <div>
                 <SectionHeader title="Instance Config" icon={Cpu} />
                 <DetailGrid>
                    <DetailItem label="Instance Type" value={details.type} />
                    <DetailItem label="Architecture" value={details.architecture} />
                    <DetailItem label="Platform" value={details.platform} />
                    <DetailItem label="Key Name" value={details.key_name} />
                 </DetailGrid>
            </div>

            <div>
                <SectionHeader title="Network" icon={Globe} />
                <DetailGrid>
                     <DetailItem label="Public IP" value={details.public_ip || 'N/A'} />
                     <DetailItem label="Private IP" value={details.private_ip} />
                     <DetailItem label="VPC ID" value={details.vpc_id} />
                     <DetailItem label="Subnet" value={details.subnet_id} />
                     <DetailItem label="Availability Zone" value={details.availability_zone} />
                </DetailGrid>
            </div>

            <div>
                <SectionHeader title="Metadata" icon={Tag} />
                 <DetailGrid>
                    <DetailItem label="Launch Time" value={new Date(details.launch_time).toLocaleString()} fullWidth />
                 </DetailGrid>
                 {details.tags && Object.keys(details.tags).length > 0 && (
                     <div className="mt-3 flex flex-wrap gap-2">
                         {Object.entries(details.tags).map(([k, v]) => (
                             <span key={k} className="inline-flex items-center px-2 py-1 rounded bg-slate-50 border border-slate-200 text-xs text-slate-600">
                                 <span className="font-semibold mr-1">{k}:</span> {String(v)}
                             </span>
                         ))}
                     </div>
                 )}
            </div>
        </>
    );
}

function EBSDetails({ details }: { details: any }) {
    return (
        <>
           <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                    <dt className="text-xs font-medium text-slate-500 mb-1">State</dt>
                    <dd><StatusBadge status={details.state} /></dd>
                </div>
            </div>

            <div>
                <SectionHeader title="Volume Config" icon={HardDrive} />
                <DetailGrid>
                    <DetailItem label="Size" value={`${details.size} GB`} />
                    <DetailItem label="Type" value={details.type} />
                    <DetailItem label="IOPS" value={details.iops} />
                    <DetailItem label="Throughput" value={details.throughput ? `${details.throughput} MB/s` : 'N/A'} />
                    <DetailItem label="Encrypted" value={details.encrypted ? 'Yes' : 'No'} />
                     <DetailItem label="Availability Zone" value={details.availability_zone} />
                </DetailGrid>
            </div>

             {details.attachments && details.attachments.length > 0 && (
                 <div>
                    <SectionHeader title="Attachments" icon={Server} />
                    <div className="space-y-2">
                        {details.attachments.map((att: any, idx: number) => (
                             <div key={idx} className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-sm">
                                <div className="font-medium text-slate-900">{att.instance_id}</div>
                                <div className="text-xs text-slate-500 mt-0.5">Device: {att.device} • {att.state}</div>
                             </div>
                        ))}
                    </div>
                 </div>
             )}
        </>
    );
}

function S3Details({ details }: { details: any }) {
    return (
        <>
             <div>
                <SectionHeader title="Storage Metrics" icon={Database} />
                <DetailGrid>
                    <DetailItem label="Total Size" value={`${details.total_size_mb} MB`} />
                    <DetailItem label="Object Count" value={details.object_count} />
                    <DetailItem label="Region" value={details.location} />
                    <DetailItem label="Created" value={new Date(details.creation_date).toLocaleDateString()} />
                </DetailGrid>
             </div>

             <div>
                <SectionHeader title="Configuration" icon={Shield} />
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 flex items-center justify-between">
                         <span className="text-sm font-medium text-slate-600">Versioning</span>
                         <StatusBadge status={details.versioning_status || 'Disabled'} />
                    </div>
                     <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 flex items-center justify-between">
                         <span className="text-sm font-medium text-slate-600">Encryption</span>
                         <StatusBadge status={details.encryption_enabled ? 'Enabled' : 'Disabled'} />
                    </div>
                </div>
             </div>
        </>
    );
}

function IAMRoleDetails({ details }: { details: any }) {
    return (
        <>
             <div>
                <SectionHeader title="Role Info" icon={Shield} />
                <DetailGrid>
                    <DetailItem label="Name" value={details.name} />
                    <DetailItem label="Created" value={new Date(details.create_date).toLocaleDateString()} />
                    <DetailItem label="Max Session" value={`${details.max_session_duration / 3600} hours`} />
                    <DetailItem label="ARN" value={details.arn} fullWidth />
                </DetailGrid>
             </div>

             <div>
                <SectionHeader title="Activity" icon={Activity} />
                <DetailGrid>
                     <DetailItem label="Last Used" value={details.last_used_date ? new Date(details.last_used_date).toLocaleString() : 'Never'} />
                     <DetailItem label="Last Region" value={details.last_used_region || 'N/A'} />
                </DetailGrid>
             </div>
        </>
    );
}

function IAMUserDetails({ details }: { details: any }) {
   return (
        <>
             <div>
                <SectionHeader title="User Info" icon={Users} />
                <DetailGrid>
                    <DetailItem label="Name" value={details.name} />
                    <DetailItem label="Created" value={new Date(details.create_date).toLocaleDateString()} />
                    <DetailItem label="Console Access" value={details.has_console_access ? 'Yes' : 'No'} />
                     <DetailItem label="ARN" value={details.arn} fullWidth />
                </DetailGrid>
             </div>

             {details.access_keys && details.access_keys.length > 0 && (
                <div>
                     <SectionHeader title="Access Keys" icon={Key} />
                     <div className="space-y-2">
                        {details.access_keys.map((key: any, idx: number) => (
                             <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100 text-sm">
                                 <div>
                                    <div className="font-mono text-slate-700">{key.access_key_id}</div>
                                    <div className="text-xs text-slate-500 mt-0.5">Created: {new Date(key.create_date).toLocaleDateString()}</div>
                                 </div>
                                 <StatusBadge status={key.status} />
                             </div>
                        ))}
                     </div>
                </div>
             )}
        </>
    );
}