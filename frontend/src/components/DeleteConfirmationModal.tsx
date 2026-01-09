"use client";

import { useState } from 'react';
import { 
  AlertTriangle, 
  Trash2, 
  X, 
  AlertOctagon,
  Loader2
} from 'lucide-react';

import { ResourceType } from '@/lib/api/types';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (force?: boolean) => Promise<void>;
  resourceType: ResourceType;
  resourceName: string;
  resourceId: string;
  showForceOption?: boolean;
}

export default function DeleteConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  resourceType,
  resourceName,
  resourceId,
  showForceOption = false
}: DeleteConfirmationModalProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [force, setForce] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  if (!isOpen) return null;

  const getResourceTypeLabel = () => {
    switch (resourceType) {
      case 'ec2': return 'EC2 Instance';
      case 'ebs': return 'EBS Volume';
      case 's3': return 'S3 Bucket';
      case 'iam-role': return 'IAM Role';
      case 'iam-user': return 'IAM User';
      default: return 'Resource';
    }
  };

  const getWarningMessage = () => {
    switch (resourceType) {
      case 'ec2':
        return 'This will permanently terminate the EC2 instance. All data on instance store volumes will be lost.';
      case 'ebs':
        return 'This will permanently delete the EBS volume. Make sure you have a snapshot if you need to recover the data.';
      case 's3':
        return force
          ? 'This will permanently delete the S3 bucket and ALL objects inside it. This action cannot be undone.'
          : 'This will permanently delete the S3 bucket. The bucket must be empty to delete.';
      case 'iam-role':
        return force
          ? 'This will permanently delete the IAM role and detach all policies. Services using this role will lose access.'
          : 'This will permanently delete the IAM role. All policies must be detached first.';
      case 'iam-user':
        return force
          ? 'This will permanently delete the IAM user, all access keys, and remove from all groups.'
          : 'This will permanently delete the IAM user. All access keys and group memberships must be removed first.';
      default:
        return 'This action cannot be undone.';
    }
  };

  const handleConfirm = async () => {
    if (confirmText !== 'DELETE') {
      return;
    }

    setIsDeleting(true);
    try {
      await onConfirm(force);
      setConfirmText('');
      setForce(false);
      onClose();
    } catch {
      // Error handling is done in parent component
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClose = () => {
    if (!isDeleting) {
      setConfirmText('');
      setForce(false);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-[100] overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen p-4 text-center sm:block sm:p-0">
        {/* Background overlay with blur - matches ResourceDetailsModal style */}
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"
          onClick={handleClose}
        />

        {/* Center alignment helper */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        {/* Modal panel */}
        <div className="relative inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full border border-slate-200">
          
          {/* Header - Clean style matching updated UI */}
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white">
             <div className="flex items-center gap-3">
                <div className="p-2 bg-red-50 rounded-lg border border-red-100 text-red-600">
                   <Trash2 className="w-5 h-5" />
                </div>
                <div>
                   <h3 className="text-lg font-semibold text-slate-900 leading-tight">Delete Resource</h3>
                   <p className="text-xs text-slate-500 font-medium">This action cannot be undone</p>
                </div>
             </div>
             <button
               onClick={handleClose}
               disabled={isDeleting}
               className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors disabled:opacity-50"
             >
               <X className="w-5 h-5" />
             </button>
          </div>

          {/* Content */}
          <div className="px-6 py-6 space-y-6">
            
             {/* Warning Box */}
             <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
                <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                   <p className="text-sm font-semibold text-red-900">Warning</p>
                   <p className="text-sm text-red-700 leading-relaxed">
                      {getWarningMessage()}
                   </p>
                </div>
             </div>

             {/* Disclaimer */}
             <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg">
                <div className="flex gap-3">
                   <AlertOctagon className="w-5 h-5 text-amber-500 shrink-0" />
                   <div>
                      <p className="text-sm text-amber-900">
                         <span className="font-semibold">Disclaimer:</span> This action triggers a real deletion in your AWS account. It cannot be undone and data will be permanently lost.
                      </p>
                   </div>
                </div>
             </div>

             {/* Resource Info Card */}
             <div className="bg-slate-50 rounded-lg border border-slate-200 p-4 space-y-3">
                <div className="flex justify-between items-center text-sm">
                   <span className="text-slate-500 font-medium">Type</span>
                   <span className="text-slate-900 font-semibold bg-white px-2 py-0.5 rounded border border-slate-200 shadow-sm">{getResourceTypeLabel()}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                   <span className="text-slate-500 font-medium">Name</span>
                   <span className="text-slate-900 font-mono break-all text-right ml-4">{resourceName}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                   <span className="text-slate-500 font-medium">ID</span>
                   <span className="text-slate-900 font-mono text-xs bg-slate-200/50 px-1.5 py-0.5 rounded">{resourceId}</span>
                </div>
             </div>

             {/* Force Option */}
             {showForceOption && (
                <div className="flex items-start p-3 bg-red-50/50 rounded-lg border border-red-100">
                   <div className="flex items-center h-5">
                      <input
                         type="checkbox"
                         id="force-delete"
                         checked={force}
                         onChange={(e) => setForce(e.target.checked)}
                         disabled={isDeleting}
                         className="focus:ring-red-500 h-4 w-4 text-red-600 border-slate-300 rounded"
                      />
                   </div>
                   <div className="ml-3 text-sm">
                      <label htmlFor="force-delete" className="font-medium text-slate-900 select-none cursor-pointer">
                         Force delete
                      </label>
                      <p className="text-slate-500 mt-0.5 leading-tight">
                        {resourceType === 's3' && 'Delete all objects in the bucket before deleting the bucket'}
                        {resourceType === 'iam-role' && 'Detach all policies and remove from instance profiles'}
                        {resourceType === 'iam-user' && 'Delete all access keys and remove from all groups'}
                      </p>
                   </div>
                </div>
             )}

             {/* Confirmation Input */}
             <div>
                <label htmlFor="confirm-text" className="block text-sm font-medium text-slate-700 mb-2">
                   Type <span className="font-mono font-bold text-red-600 bg-red-50 px-1 rounded border border-red-100">DELETE</span> to confirm:
                </label>
                <input
                   type="text"
                   id="confirm-text"
                   value={confirmText}
                   onChange={(e) => setConfirmText(e.target.value)}
                   disabled={isDeleting}
                   placeholder="DELETE"
                   className="w-full px-4 py-2.5 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-slate-50 disabled:text-slate-400 transition-all font-mono shadow-sm"
                />
             </div>
          </div>

          {/* Footer */}
          <div className="bg-slate-50 px-6 py-4 flex justify-end gap-3 border-t border-slate-100">
             <button
               onClick={handleClose}
               disabled={isDeleting}
               className="px-4 py-2 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
             >
               Cancel
             </button>
             <button
               onClick={handleConfirm}
               disabled={isDeleting || confirmText !== 'DELETE'}
               className="px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm shadow-red-200"
             >
               {isDeleting ? (
                 <>
                   <Loader2 className="w-4 h-4 animate-spin" />
                   Deleting...
                 </>
               ) : (
                 <>
                   <Trash2 className="w-4 h-4" />
                   Delete Resource
                 </>
               )}
             </button>
          </div>

        </div>
      </div>
    </div>
  );
}