"use client";

import { useState } from 'react';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (force?: boolean) => Promise<void>;
  resourceType: 'ec2' | 'ebs' | 's3' | 'iam-role' | 'iam-user';
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
      case 'ec2':
        return 'EC2 Instance';
      case 'ebs':
        return 'EBS Volume';
      case 's3':
        return 'S3 Bucket';
      case 'iam-role':
        return 'IAM Role';
      case 'iam-user':
        return 'IAM User';
      default:
        return 'Resource';
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
    } catch (error) {
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
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-900 bg-opacity-75"
          onClick={handleClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          {/* Header */}
          <div className="bg-red-600 px-6 py-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg
                  className="h-6 w-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-semibold text-white">
                Delete {getResourceTypeLabel()}
              </h3>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4">
            <div className="space-y-4">
              {/* Warning message */}
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">
                  <strong>Warning:</strong> {getWarningMessage()}
                </p>
              </div>

              {/* Resource info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">Type:</span>
                    <span className="text-sm text-gray-900">{getResourceTypeLabel()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">Name:</span>
                    <span className="text-sm text-gray-900 font-mono">{resourceName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">ID:</span>
                    <span className="text-sm text-gray-900 font-mono">{resourceId}</span>
                  </div>
                </div>
              </div>

              {/* Force option */}
              {showForceOption && (
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="force-delete"
                    checked={force}
                    onChange={(e) => setForce(e.target.checked)}
                    disabled={isDeleting}
                    className="mt-1 h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                  />
                  <label htmlFor="force-delete" className="ml-3 text-sm text-gray-700">
                    <span className="font-medium">Force delete</span>
                    <p className="text-gray-500 mt-1">
                      {resourceType === 's3' && 'Delete all objects in the bucket before deleting the bucket'}
                      {resourceType === 'iam-role' && 'Detach all policies and remove from instance profiles'}
                      {resourceType === 'iam-user' && 'Delete all access keys and remove from all groups'}
                    </p>
                  </label>
                </div>
              )}

              {/* Confirmation input */}
              <div>
                <label htmlFor="confirm-text" className="block text-sm font-medium text-gray-700 mb-2">
                  Type <span className="font-mono font-bold">DELETE</span> to confirm:
                </label>
                <input
                  type="text"
                  id="confirm-text"
                  value={confirmText}
                  onChange={(e) => setConfirmText(e.target.value)}
                  disabled={isDeleting}
                  placeholder="DELETE"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3">
            <button
              onClick={handleClose}
              disabled={isDeleting}
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={isDeleting || confirmText !== 'DELETE'}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isDeleting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Deleting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Delete {getResourceTypeLabel()}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}