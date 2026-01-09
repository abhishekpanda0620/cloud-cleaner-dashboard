'use client';

import { useState, useEffect } from 'react';
import { Clock, Bell, Mail, MessageSquare, Play, RefreshCw, Calendar, AlertTriangle, CheckCircle2 } from 'lucide-react';

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
      <div className="bg-white rounded-lg border border-slate-200 p-6 animate-pulse">
        <div className="h-6 bg-slate-100 rounded w-1/3 mb-4"></div>
        <div className="h-24 bg-slate-100 rounded mb-4"></div>
        <div className="h-10 bg-slate-100 rounded w-full"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="w-5 h-5 text-slate-500" />
          <h3 className="font-semibold text-slate-900">Scan Schedule</h3>
        </div>
        
        <div className="flex items-center gap-2">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${config.enabled ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
                {config.enabled ? 'Active' : 'Disabled'}
            </span>
            <button
                onClick={() => handleToggle(!config.enabled)}
                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                config.enabled ? 'bg-blue-600' : 'bg-slate-200'
                }`}
            >
                <span
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    config.enabled ? 'translate-x-4' : 'translate-x-0'
                }`}
                />
            </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-center gap-2 text-sm text-red-700">
                <AlertTriangle className="w-4 h-4" />
                {error}
            </div>
        )}

        {success && (
             <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-md flex items-center gap-2 text-sm text-emerald-700">
                <CheckCircle2 className="w-4 h-4" />
                {success}
            </div>
        )}

        {/* Configuration Form */}
        <div className={`space-y-6 transition-opacity duration-200 ${!config.enabled ? 'opacity-50 pointer-events-none' : ''}`}>
             {/* Frequency */}
             <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Frequency</label>
                <select
                    value={config.frequency}
                    onChange={(e) => setConfig({ ...config, frequency: e.target.value })}
                    className="block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                    disabled={!config.enabled}
                >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="custom">Custom Interval</option>
                </select>
            </div>

            {config.frequency === 'custom' && (
                <div>
                   <label className="block text-sm font-medium text-slate-700 mb-2">Interval (minutes)</label>
                   <input
                        type="number"
                        min="1"
                        value={config.custom_interval || 60}
                        onChange={(e) => setConfig({ ...config, custom_interval: parseInt(e.target.value) })}
                        className="block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                   />
                </div>
            )}

            {/* Channels */}
            <div>
                 <label className="block text-sm font-medium text-slate-700 mb-2">Notifications</label>
                 <div className="space-y-2">
                    <label className="flex items-center gap-2 p-2 rounded hover:bg-slate-50 border border-transparent hover:border-slate-200 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={config.channels.includes('slack')}
                            onChange={() => handleChannelToggle('slack')}
                            className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                            disabled={!config.enabled}
                        />
                        <MessageSquare className="w-4 h-4 text-slate-500" />
                        <span className="text-sm text-slate-700">Slack</span>
                    </label>
                    <label className="flex items-center gap-2 p-2 rounded hover:bg-slate-50 border border-transparent hover:border-slate-200 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={config.channels.includes('email')}
                            onChange={() => handleChannelToggle('email')}
                            className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                             disabled={!config.enabled}
                        />
                        <Mail className="w-4 h-4 text-slate-500" />
                        <span className="text-sm text-slate-700">Email</span>
                    </label>
                 </div>
            </div>

             <div className="pt-4 border-t border-slate-100 flex justify-end">
                <button
                    onClick={handleSave}
                    disabled={saving || !config.enabled}
                    className="inline-flex items-center gap-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-slate-300 disabled:cursor-not-allowed"
                >
                    {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Bell className="w-4 h-4" />}
                    {saving ? 'Saving...' : 'Update Schedule'}
                </button>
            </div>
        </div>

        {/* Footer Status */}
        {status && (
            <div className="bg-slate-50 rounded-md p-3 text-xs text-slate-500 flex justify-between items-center border border-slate-100">
                <span>Last scan: {formatDateTime(status.last_scan)}</span>
                <span>Next: {config.enabled ? formatDateTime(status.next_scan) : 'Paused'}</span>
            </div>
        )}
      </div>
    </div>
  );
}