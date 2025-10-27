import { useState } from 'react';
import NotificationSetupGuide from './NotificationSetupGuide';

interface AlertPanelProps {
  s3Count: number;
  iamUsersCount: number;
  onAlertSent?: () => void;
}

export default function AlertPanel({ s3Count, iamUsersCount, onAlertSent }: AlertPanelProps) {
  const [loadingSlack, setLoadingSlack] = useState(false);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');
  const [showSetupGuide, setShowSetupGuide] = useState(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8084/api";

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
          count: s3Count + iamUsersCount, // Total global resources
          estimated_savings: 0,
          channel: channel,
          details: {
            s3_count: s3Count,
            iam_users_count: iamUsersCount
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
      
      // Show success message with background processing info
      let successMessage = `✓ Alert queued! ${result.message || 'Processing in background...'}`;
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
    <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl shadow-lg p-6 mb-8 text-white">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-2xl font-bold">Send Resource Alerts</p>
          <p className="text-sm text-green-100 mt-2">Notify your team about unused AWS resources via Slack or Email</p>
        </div>
        <div className="h-20 w-20 bg-white/20 rounded-lg flex items-center justify-center">
          <span className="text-5xl">📢</span>
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
      <div className="flex gap-3 mb-4">
        <button
          onClick={() => sendAlert('slack')}
          disabled={loadingSlack || loadingEmail}
          className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
            loadingSlack || loadingEmail
              ? 'bg-white/30 text-white/50 cursor-not-allowed'
              : 'bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm'
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
          disabled={loadingSlack || loadingEmail}
          className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
            loadingSlack || loadingEmail
              ? 'bg-white/30 text-white/50 cursor-not-allowed'
              : 'bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm'
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
        <button
          onClick={() => setShowSetupGuide(true)}
          className="px-4 py-3 rounded-lg font-medium bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm transition-colors"
          title="Setup Guide"
        >
          📖
        </button>
      </div>

      {/* Setup Guide Modal */}
      <NotificationSetupGuide
        isOpen={showSetupGuide}
        onClose={() => setShowSetupGuide(false)}
      />
    </div>
  );
}