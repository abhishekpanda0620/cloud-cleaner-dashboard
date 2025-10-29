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
    <div className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-pink-600 to-rose-600 rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-300">
      {/* Animated background pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent"></div>
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
      <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-purple-900/20 rounded-full blur-3xl"></div>
      
      <div className="relative p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="h-12 w-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">📢</span>
              </div>
              <h2 className="text-3xl font-bold text-white drop-shadow-lg">
                Send Resource Alerts
              </h2>
            </div>
            <p className="text-white/90 text-sm ml-15 backdrop-blur-sm">
              Notify your team about unused AWS resources via Slack or Email
            </p>
          </div>
          <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
            <span className="text-2xl">📊</span>
            <div className="text-right">
              <div className="text-xs text-white/70 uppercase tracking-wide">Total Resources</div>
              <div className="text-2xl font-bold text-white">{s3Count + iamUsersCount}</div>
            </div>
          </div>
        </div>

        {/* Message Display */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-xl border-2 backdrop-blur-sm shadow-lg transform transition-all duration-300 ${
              messageType === 'success'
                ? 'bg-green-500/20 border-green-300/50 text-white'
                : 'bg-red-500/20 border-red-300/50 text-white'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{messageType === 'success' ? '✓' : '⚠'}</span>
              <p className="text-sm font-medium">{message}</p>
            </div>
          </div>
        )}

        {/* Send Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => sendAlert('slack')}
            disabled={loadingSlack || loadingEmail}
            className={`group relative overflow-hidden px-6 py-4 rounded-xl font-semibold transition-all duration-300 transform hover:-translate-y-1 ${
              loadingSlack || loadingEmail
                ? 'bg-white/20 text-white/50 cursor-not-allowed'
                : 'bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 shadow-lg hover:shadow-xl border border-white/30'
            }`}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            {loadingSlack ? (
              <span className="relative flex items-center justify-center gap-2">
                <span className="inline-block h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Sending...
              </span>
            ) : (
              <span className="relative flex items-center justify-center gap-2">
                <span className="text-2xl group-hover:scale-110 transition-transform duration-300">💬</span>
                <span>Send to Slack</span>
              </span>
            )}
          </button>
          
          <button
            onClick={() => sendAlert('email')}
            disabled={loadingSlack || loadingEmail}
            className={`group relative overflow-hidden px-6 py-4 rounded-xl font-semibold transition-all duration-300 transform hover:-translate-y-1 ${
              loadingSlack || loadingEmail
                ? 'bg-white/20 text-white/50 cursor-not-allowed'
                : 'bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 shadow-lg hover:shadow-xl border border-white/30'
            }`}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            {loadingEmail ? (
              <span className="relative flex items-center justify-center gap-2">
                <span className="inline-block h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Sending...
              </span>
            ) : (
              <span className="relative flex items-center justify-center gap-2">
                <span className="text-2xl group-hover:scale-110 transition-transform duration-300">📧</span>
                <span>Send to Email</span>
              </span>
            )}
          </button>
          
          <button
            onClick={() => setShowSetupGuide(true)}
            className="group relative overflow-hidden px-6 py-4 rounded-xl font-semibold bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 transition-all duration-300 transform hover:-translate-y-1 shadow-lg hover:shadow-xl border border-white/30"
            title="Setup Guide"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-amber-400/20 to-orange-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <span className="relative flex items-center justify-center gap-2">
              <span className="text-2xl group-hover:scale-110 transition-transform duration-300">📖</span>
              <span>Setup Guide</span>
            </span>
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