import { useState } from 'react';
import NotificationSetupGuide from './NotificationSetupGuide';

interface AlertPanelProps {
  resourceCounts: {
    ec2: number;
    ebs: number;
    s3: number;
    iam_users: number;
    access_keys: number;
  };
  onAlertSent?: () => void;
}

export default function AlertPanel({ resourceCounts, onAlertSent }: AlertPanelProps) {
  const [loadingSlack, setLoadingSlack] = useState(false);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');
  const [showSetupGuide, setShowSetupGuide] = useState(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8084/api";

  const totalResources = Object.values(resourceCounts).reduce((a, b) => a + b, 0);
  const estimatedSavings = (resourceCounts.ec2 * 50) + (resourceCounts.ebs * 10) + (resourceCounts.s3 * 5);

  const sendAlert = async (channel: 'slack' | 'email') => {
    try {
      if (channel === 'slack') {
        setLoadingSlack(true);
      } else {
        setLoadingEmail(true);
      }
      setMessage('');
      setMessageType('');

      const response = await fetch(`${apiUrl}/notifications/send-alert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resource_type: 'unused_resources',
          count: totalResources,
          estimated_savings: estimatedSavings,
          channel: channel,
          details: {
            ec2_count: resourceCounts.ec2,
            ebs_count: resourceCounts.ebs,
            s3_count: resourceCounts.s3,
            iam_users_count: resourceCounts.iam_users,
            access_keys_count: resourceCounts.access_keys,
            total_savings: estimatedSavings
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to send alert to ${channel}`);
      }

      const result = await response.json();
      
      // Check if the specific channel was actually sent
      const channelSent = channel === 'slack' ? result.slack_sent : result.email_sent;
      
      if (!channelSent) {
        throw new Error(`${channel === 'slack' ? 'Slack' : 'Email'} is not configured. Please check your environment variables.`);
      }
      
      let successMessage = `✓ Alert sent to ${channel === 'slack' ? 'Slack' : 'Email'}!`;
      setMessage(successMessage);
      setMessageType('success');
      onAlertSent?.();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : `Failed to send alert to ${channel}`);
      setMessageType('error');
    } finally {
      if (channel === 'slack') {
        setLoadingSlack(false);
      } else {
        setLoadingEmail(false);
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Send Alert</h2>
          <p className="text-sm text-slate-600 mt-1">
            Send a summary of unused resources to Slack or Email
          </p>
        </div>
        <div className="text-4xl">🔔</div>
      </div>

      {/* Resource Summary */}
      <div className="bg-slate-50 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <p className="text-xs text-slate-600 uppercase font-semibold">EC2</p>
            <p className="text-2xl font-bold text-slate-900">{resourceCounts.ec2}</p>
          </div>
          <div>
            <p className="text-xs text-slate-600 uppercase font-semibold">EBS</p>
            <p className="text-2xl font-bold text-slate-900">{resourceCounts.ebs}</p>
          </div>
          <div>
            <p className="text-xs text-slate-600 uppercase font-semibold">S3</p>
            <p className="text-2xl font-bold text-slate-900">{resourceCounts.s3}</p>
          </div>
          <div>
            <p className="text-xs text-slate-600 uppercase font-semibold">Users</p>
            <p className="text-2xl font-bold text-slate-900">{resourceCounts.iam_users}</p>
          </div>
          <div>
            <p className="text-xs text-slate-600 uppercase font-semibold">Keys</p>
            <p className="text-2xl font-bold text-slate-900">{resourceCounts.access_keys}</p>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-slate-200">
          <p className="text-sm text-slate-600">
            <span className="font-semibold text-slate-900">{totalResources}</span> total unused resources
          </p>
          <p className="text-sm text-green-600 font-semibold mt-1">
            💰 Potential savings: ${estimatedSavings.toFixed(2)}/month
          </p>
        </div>
      </div>

      {/* Message Display */}
      {message && (
        <div
          className={`mb-6 p-4 rounded-lg border ${
            messageType === 'success'
              ? 'bg-green-50 border-green-200 text-green-800'
              : 'bg-red-50 border-red-200 text-red-800'
          }`}
        >
          <p className="text-sm font-medium">{message}</p>
        </div>
      )}

      {/* Send Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => sendAlert('slack')}
          disabled={loadingSlack || loadingEmail || totalResources === 0}
          className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
            loadingSlack || loadingEmail || totalResources === 0
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
              : 'bg-purple-600 text-white hover:bg-purple-700'
          }`}
        >
          {loadingSlack ? (
            <span className="flex items-center justify-center gap-2">
              <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              Sending...
            </span>
          ) : (
            '💬 Send to Slack'
          )}
        </button>
        <button
          onClick={() => sendAlert('email')}
          disabled={loadingSlack || loadingEmail || totalResources === 0}
          className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
            loadingSlack || loadingEmail || totalResources === 0
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {loadingEmail ? (
            <span className="flex items-center justify-center gap-2">
              <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              Sending...
            </span>
          ) : (
            '📧 Send to Email'
          )}
        </button>
      </div>

      {totalResources === 0 && (
        <p className="text-sm text-slate-500 mt-3 text-center">
          No unused resources to report
        </p>
      )}

      {/* Info Box with Setup Guide */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start justify-between gap-4">
          <p className="text-sm text-blue-800">
            <span className="font-semibold">ℹ️ Need help setting up?</span> Click the button to see step-by-step instructions for Slack and Email notifications.
          </p>
          <button
            onClick={() => setShowSetupGuide(true)}
            className="flex-shrink-0 px-3 py-1 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors whitespace-nowrap"
          >
            📖 Setup Guide
          </button>
        </div>
      </div>

      {/* Setup Guide Modal */}
      <NotificationSetupGuide
        isOpen={showSetupGuide}
        onClose={() => setShowSetupGuide(false)}
      />
    </div>
  );
}