'use client';

import { useState } from 'react';

interface NotificationSetupGuideProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function NotificationSetupGuide({ isOpen, onClose }: NotificationSetupGuideProps) {
  const [activeTab, setActiveTab] = useState<'slack' | 'email'>('slack');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">🔔 Setup Notifications</h2>
            <p className="text-blue-100 mt-1">Get alerts about unused AWS resources</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-blue-800 rounded-lg p-2 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-200">
          <button
            onClick={() => setActiveTab('slack')}
            className={`flex-1 py-4 px-6 font-medium transition-colors ${
              activeTab === 'slack'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            💬 Slack Setup
          </button>
          <button
            onClick={() => setActiveTab('email')}
            className={`flex-1 py-4 px-6 font-medium transition-colors ${
              activeTab === 'email'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            📧 Email Setup
          </button>
        </div>

        {/* Content */}
        <div className="p-8">
          {activeTab === 'slack' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  💡 <strong>Tip:</strong> You'll need a Slack workspace and admin access to create a webhook.
                </p>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 1: Create a Slack App</h3>
                <ol className="space-y-3 ml-4">
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
                    <span className="text-slate-700">Go to <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Slack Apps</a> and click <strong>"Create New App"</strong></span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
                    <span className="text-slate-700">Select <strong>"From scratch"</strong></span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
                    <span className="text-slate-700">Name your app (e.g., <strong>"Cloud Cleaner"</strong>) and select your workspace</span>
                  </li>
                </ol>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 2: Enable Incoming Webhooks</h3>
                <ol className="space-y-3 ml-4">
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
                    <span className="text-slate-700">In the left menu, click <strong>"Incoming Webhooks"</strong></span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
                    <span className="text-slate-700">Toggle <strong>"Activate Incoming Webhooks"</strong> to ON</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
                    <span className="text-slate-700">Click <strong>"Add New Webhook to Workspace"</strong></span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">4</span>
                    <span className="text-slate-700">Select the channel where you want to receive alerts</span>
                  </li>
                </ol>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 3: Copy Your Webhook URL</h3>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                  <p className="text-sm text-slate-700 mb-2">You'll see a URL like this:</p>
                  <code className="text-xs bg-slate-900 text-green-400 p-3 rounded block overflow-x-auto">
                    https://hooks.slack.com/services/YOUR/WEBHOOK/URL
                  </code>
                  <p className="text-sm text-slate-600 mt-2">Copy this entire URL</p>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 4: Add to Cloud Cleaner</h3>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-900 mb-3">Add this to your <strong>.env</strong> file:</p>
                  <code className="text-xs bg-slate-900 text-green-400 p-3 rounded block overflow-x-auto">
                    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
                  </code>
                  <p className="text-sm text-green-900 mt-3">Then restart the backend:</p>
                  <code className="text-xs bg-slate-900 text-green-400 p-3 rounded block overflow-x-auto mt-2">
                    docker-compose restart backend
                  </code>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-900">
                  ⚠️ <strong>Important:</strong> Keep your webhook URL secret! Don't share it or commit it to version control.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'email' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  💡 <strong>Tip:</strong> We recommend using Gmail for testing. You can use any SMTP server (Office 365, SendGrid, etc.)
                </p>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 1: Get Your Email Credentials</h3>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
                  <div>
                    <p className="font-medium text-slate-900 mb-1">📧 For Gmail:</p>
                    <ol className="space-y-2 ml-4 text-sm text-slate-700">
                      <li>1. Enable <a href="https://myaccount.google.com/security" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">2-Factor Authentication</a></li>
                      <li>2. Generate an <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">App Password</a></li>
                      <li>3. Use the generated 16-character password</li>
                    </ol>
                  </div>
                  <div className="border-t border-slate-200 pt-3">
                    <p className="font-medium text-slate-900 mb-1">🏢 For Office 365:</p>
                    <p className="text-sm text-slate-700">Use your regular Office 365 password</p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 2: Configure Email Recipients</h3>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-900 mb-2">Add email addresses that should receive alerts:</p>
                  <code className="text-xs bg-slate-900 text-green-400 p-3 rounded block overflow-x-auto">
                    NOTIFICATION_EMAIL_RECIPIENTS=admin@company.com,devops@company.com
                  </code>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 3: Add SMTP Configuration</h3>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-900 mb-2">Add these to your <strong>.env</strong> file:</p>
                  <code className="text-xs bg-slate-900 text-green-400 p-3 rounded block overflow-x-auto">
{`# For Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com

# For Office 365
# SMTP_SERVER=smtp.office365.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@company.com
# SMTP_PASSWORD=your-password
# SENDER_EMAIL=your-email@company.com`}
                  </code>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Step 4: Restart Backend</h3>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-900 mb-2">Restart the backend to apply changes:</p>
                  <code className="text-xs bg-slate-900 text-green-400 p-3 rounded block overflow-x-auto">
                    docker-compose restart backend
                  </code>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-900">
                  ⚠️ <strong>Important:</strong> Never commit your .env file to version control. Keep your credentials secure!
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 bg-slate-50 p-6 flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-slate-200 text-slate-900 rounded-lg font-medium hover:bg-slate-300 transition-colors"
          >
            Close
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Got it! 👍
          </button>
        </div>
      </div>
    </div>
  );
}