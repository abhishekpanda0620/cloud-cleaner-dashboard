'use client';

import { useState, useEffect } from 'react';
import { Clock, Bell, Mail, MessageSquare, Play, Pause, RefreshCw } from 'lucide-react';

interface ScheduleConfig {
  enabled: boolean;
  frequency: string;
  channels: string[];
  custom_interval?: number;
}

interface ScheduleStatus {
  enabled: boolean;
  frequency: string;
  channels: string[];
  last_scan: string | null;
  next_scan: string | null;
}

export default function ScheduleSettings() {
  const [config, setConfig] = useState<ScheduleConfig>({
    enabled: false,
    frequency: 'daily',
    channels: [],
    custom_interval: 60,
  });
  const [status, setStatus] = useState<ScheduleStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

  useEffect(() => {
    fetchConfig();
    fetchStatus();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/schedule/config`);
      if (!response.ok) throw new Error('Failed to fetch schedule config');
      const data = await response.json();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/schedule/status`);
      if (!response.ok) throw new Error('Failed to fetch schedule status');
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_URL}/schedule/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save configuration');
      }

      setSuccess('Schedule settings saved successfully!');
      await fetchStatus();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (enabled: boolean) => {
    setError(null);
    setSuccess(null);

    try {
      const endpoint = enabled ? 'enable' : 'disable';
      const response = await fetch(`${API_URL}/schedule/${endpoint}`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error(`Failed to ${endpoint} schedule`);

      setConfig({ ...config, enabled });
      setSuccess(`Scheduled scans ${enabled ? 'enabled' : 'disabled'}!`);
      await fetchStatus();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle schedule');
    }
  };

  const handleTriggerNow = async () => {
    setTriggering(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_URL}/schedule/trigger`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to trigger scan');

      setSuccess('Scan triggered successfully! Check notifications for results.');
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger scan');
    } finally {
      setTriggering(false);
    }
  };

  const handleChannelToggle = (channel: string) => {
    const newChannels = config.channels.includes(channel)
      ? config.channels.filter(c => c !== channel)
      : [...config.channels, channel];
    setConfig({ ...config, channels: newChannels });
  };

  const formatDateTime = (isoString: string | null) => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="relative overflow-hidden bg-white rounded-2xl shadow-xl border border-slate-200/50 p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gradient-to-r from-slate-200 to-slate-300 rounded-xl w-1/3 mb-6"></div>
          <div className="space-y-4">
            <div className="h-6 bg-slate-200 rounded-lg"></div>
            <div className="h-6 bg-slate-200 rounded-lg w-5/6"></div>
            <div className="h-6 bg-slate-200 rounded-lg w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden bg-white rounded-2xl shadow-xl border border-slate-200/50 hover:shadow-2xl transition-all duration-300">
      {/* Decorative gradient background */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full blur-3xl opacity-30 -z-10"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-purple-100 to-pink-100 rounded-full blur-3xl opacity-30 -z-10"></div>
      
      <div className="relative p-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform duration-300">
              <Clock className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Schedule Settings
              </h2>
              <p className="text-sm text-slate-600 mt-1">Automate resource scanning and notifications</p>
            </div>
          </div>
          <div className="flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-slate-50 to-slate-100 rounded-xl border border-slate-200 shadow-sm">
            <span className={`text-sm font-semibold ${config.enabled ? 'text-green-600' : 'text-slate-500'}`}>
              {config.enabled ? '● Enabled' : '○ Disabled'}
            </span>
            <button
              onClick={() => handleToggle(!config.enabled)}
              className={`relative inline-flex h-7 w-12 items-center rounded-full transition-all duration-300 shadow-inner ${
                config.enabled ? 'bg-gradient-to-r from-green-500 to-emerald-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-lg transition-transform duration-300 ${
                  config.enabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-gradient-to-r from-red-50 to-rose-50 border-2 border-red-200 rounded-xl text-red-700 text-sm shadow-md transform transition-all duration-300">
            <div className="flex items-center gap-2">
              <span className="text-xl">⚠</span>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl text-green-700 text-sm shadow-md transform transition-all duration-300">
            <div className="flex items-center gap-2">
              <span className="text-xl">✓</span>
              <span className="font-medium">{success}</span>
            </div>
          </div>
        )}

        <div className="space-y-6">
          {/* Frequency Selection */}
          <div className="group">
            <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <span className="text-lg">⏱️</span>
              Scan Frequency
            </label>
            <select
              value={config.frequency}
              onChange={(e) => setConfig({ ...config, frequency: e.target.value })}
              className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white shadow-sm hover:border-slate-300 disabled:bg-slate-50 disabled:cursor-not-allowed font-medium"
              disabled={!config.enabled}
            >
              <option value="hourly">⚡ Hourly</option>
              <option value="daily">📅 Daily</option>
              <option value="weekly">📆 Weekly</option>
              <option value="custom">⚙️ Custom</option>
            </select>
          </div>

          {/* Custom Interval */}
          {config.frequency === 'custom' && (
            <div className="group animate-in fade-in duration-300">
              <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                <span className="text-lg">🔧</span>
                Custom Interval (minutes)
              </label>
              <input
                type="number"
                min="1"
                value={config.custom_interval || 60}
                onChange={(e) => setConfig({ ...config, custom_interval: parseInt(e.target.value) })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white shadow-sm hover:border-slate-300 disabled:bg-slate-50 disabled:cursor-not-allowed font-medium"
                disabled={!config.enabled}
              />
            </div>
          )}

          {/* Notification Channels */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <span className="text-lg">📣</span>
              Notification Channels
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label className="group relative overflow-hidden flex items-center gap-3 p-4 border-2 border-slate-200 rounded-xl hover:border-purple-300 hover:bg-purple-50/50 cursor-pointer transition-all duration-300 shadow-sm hover:shadow-md transform hover:-translate-y-0.5">
                <input
                  type="checkbox"
                  checked={config.channels.includes('slack')}
                  onChange={() => handleChannelToggle('slack')}
                  className="w-5 h-5 text-purple-600 rounded-lg focus:ring-2 focus:ring-purple-500 border-2 border-slate-300"
                  disabled={!config.enabled}
                />
                <div className="h-10 w-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-300">
                  <MessageSquare className="w-5 h-5 text-white" />
                </div>
                <span className="text-sm font-semibold text-slate-700">Slack</span>
              </label>
              <label className="group relative overflow-hidden flex items-center gap-3 p-4 border-2 border-slate-200 rounded-xl hover:border-blue-300 hover:bg-blue-50/50 cursor-pointer transition-all duration-300 shadow-sm hover:shadow-md transform hover:-translate-y-0.5">
                <input
                  type="checkbox"
                  checked={config.channels.includes('email')}
                  onChange={() => handleChannelToggle('email')}
                  className="w-5 h-5 text-blue-600 rounded-lg focus:ring-2 focus:ring-blue-500 border-2 border-slate-300"
                  disabled={!config.enabled}
                />
                <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-300">
                  <Mail className="w-5 h-5 text-white" />
                </div>
                <span className="text-sm font-semibold text-slate-700">Email</span>
              </label>
            </div>
          </div>

          {/* Status Information */}
          {status && (
            <div className="pt-6 border-t-2 border-slate-200">
              <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
                <span className="text-lg">📊</span>
                Scan Status
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="group relative overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-xl border-2 border-blue-200 shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="h-8 w-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white text-sm">🕐</span>
                    </div>
                    <div className="text-xs text-slate-600 uppercase tracking-wide font-semibold">Last Scan</div>
                  </div>
                  <div className="text-base font-bold text-slate-900 ml-11">
                    {formatDateTime(status.last_scan)}
                  </div>
                </div>
                <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-50 to-teal-50 p-5 rounded-xl border-2 border-emerald-200 shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="h-8 w-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white text-sm">⏭️</span>
                    </div>
                    <div className="text-xs text-slate-600 uppercase tracking-wide font-semibold">Next Scan</div>
                  </div>
                  <div className="text-base font-bold text-slate-900 ml-11">
                    {config.enabled ? formatDateTime(status.next_scan) : 'Disabled'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t-2 border-slate-200">
            <button
              onClick={handleSave}
              disabled={saving || !config.enabled}
              className="group flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-semibold"
            >
              {saving ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Bell className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                  Save Settings
                </>
              )}
            </button>
            <button
              onClick={handleTriggerNow}
              disabled={triggering}
              className="group flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-semibold"
            >
              {triggering ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                  Scan Now
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}