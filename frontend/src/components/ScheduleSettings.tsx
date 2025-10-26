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
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-800">Schedule Settings</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">
            {config.enabled ? 'Enabled' : 'Disabled'}
          </span>
          <button
            onClick={() => handleToggle(!config.enabled)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              config.enabled ? 'bg-blue-600' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                config.enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
          {success}
        </div>
      )}

      <div className="space-y-6">
        {/* Frequency Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Scan Frequency
          </label>
          <select
            value={config.frequency}
            onChange={(e) => setConfig({ ...config, frequency: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={!config.enabled}
          >
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        {/* Custom Interval */}
        {config.frequency === 'custom' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Interval (minutes)
            </label>
            <input
              type="number"
              min="1"
              value={config.custom_interval || 60}
              onChange={(e) => setConfig({ ...config, custom_interval: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={!config.enabled}
            />
          </div>
        )}

        {/* Notification Channels */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Notification Channels
          </label>
          <div className="space-y-2">
            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={config.channels.includes('slack')}
                onChange={() => handleChannelToggle('slack')}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                disabled={!config.enabled}
              />
              <MessageSquare className="w-5 h-5 text-purple-600" />
              <span className="text-sm text-gray-700">Slack</span>
            </label>
            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={config.channels.includes('email')}
                onChange={() => handleChannelToggle('email')}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                disabled={!config.enabled}
              />
              <Mail className="w-5 h-5 text-blue-600" />
              <span className="text-sm text-gray-700">Email</span>
            </label>
          </div>
        </div>

        {/* Status Information */}
        {status && (
          <div className="border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Scan Status</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-xs text-gray-500 mb-1">Last Scan</div>
                <div className="text-sm font-medium text-gray-800">
                  {formatDateTime(status.last_scan)}
                </div>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-xs text-gray-500 mb-1">Next Scan</div>
                <div className="text-sm font-medium text-gray-800">
                  {config.enabled ? formatDateTime(status.next_scan) : 'Disabled'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t">
          <button
            onClick={handleSave}
            disabled={saving || !config.enabled}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Bell className="w-4 h-4" />
                Save Settings
              </>
            )}
          </button>
          <button
            onClick={handleTriggerNow}
            disabled={triggering}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {triggering ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Scan Now
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}