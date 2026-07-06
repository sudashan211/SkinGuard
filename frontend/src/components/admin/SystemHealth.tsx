import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Cpu, HardDrive, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface SystemHealth {
  status: string;
  timestamp: string;
  uptime: {
    seconds: number;
    hours: number;
    days: number;
    started_at: string;
  };
  cpu: {
    usage_percent: number;
    count: number;
    status: string;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
    status: string;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    free_gb: number;
    usage_percent: number;
    status: string;
  };
}

interface Service {
  name: string;
  status: string;
  message: string;
  checked_at: string;
}

interface Alert {
  id: string;
  severity: string;
  type: string;
  message: string;
  value: number;
  threshold: number;
  created_at: string;
}

const SystemHealth: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchSystemHealth();
    fetchServices();
    fetchAlerts();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchSystemHealth();
        fetchServices();
        fetchAlerts();
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchSystemHealth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/system/health`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setHealth(data);
      }
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchServices = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/system/services`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setServices(data.services || []);
      }
    } catch (error) {
      console.error('Failed to fetch services:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/system/alerts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'warning':
        return <AlertTriangle className="text-yellow-500" size={20} />;
      case 'critical':
      case 'unhealthy':
        return <XCircle className="text-red-500" size={20} />;
      default:
        return <Activity className="text-gray-500" size={20} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'critical':
      case 'unhealthy':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getProgressColor = (percent: number) => {
    if (percent < 60) return 'bg-green-500';
    if (percent < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return <div className="p-6 text-center">Loading system health...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">System Health Monitoring</h2>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">Auto-refresh (30s)</span>
          </label>
          <button
            onClick={() => {
              fetchSystemHealth();
              fetchServices();
              fetchAlerts();
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Refresh Now
          </button>
        </div>
      </div>

      {/* Overall Status */}
      {health && (
        <div className={`p-6 rounded-lg border-2 ${getStatusColor(health.status)}`}>
          <div className="flex items-center gap-3">
            {getStatusIcon(health.status)}
            <div>
              <h3 className="text-lg font-semibold">System Status: {health.status.toUpperCase()}</h3>
              <p className="text-sm">Uptime: {health.uptime.days.toFixed(1)} days ({health.uptime.hours.toFixed(1)} hours)</p>
            </div>
          </div>
        </div>
      )}

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="text-orange-500" />
            Active Alerts ({alerts.length})
          </h3>
          <div className="space-y-2">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border ${
                  alert.severity === 'critical' ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{alert.message}</p>
                    <p className="text-sm text-gray-600">
                      Current: {alert.value}% | Threshold: {alert.threshold}%
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    alert.severity === 'critical' ? 'bg-red-200 text-red-800' : 'bg-yellow-200 text-yellow-800'
                  }`}>
                    {alert.severity.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Metrics */}
      {health && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* CPU */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-4">
              <Cpu className="text-blue-500" size={24} />
              <div>
                <h3 className="font-semibold">CPU Usage</h3>
                <p className="text-sm text-gray-500">{health.cpu.count} cores</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Usage</span>
                <span className="font-medium">{health.cpu.usage_percent.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${getProgressColor(health.cpu.usage_percent)}`}
                  style={{ width: `${health.cpu.usage_percent}%` }}
                />
              </div>
              <div className="flex items-center gap-2 mt-2">
                {getStatusIcon(health.cpu.status)}
                <span className="text-sm capitalize">{health.cpu.status}</span>
              </div>
            </div>
          </div>

          {/* Memory */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-4">
              <Server className="text-purple-500" size={24} />
              <div>
                <h3 className="font-semibold">Memory Usage</h3>
                <p className="text-sm text-gray-500">{health.memory.total_gb.toFixed(1)} GB total</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Used</span>
                <span className="font-medium">{health.memory.used_gb.toFixed(1)} GB ({health.memory.usage_percent.toFixed(1)}%)</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${getProgressColor(health.memory.usage_percent)}`}
                  style={{ width: `${health.memory.usage_percent}%` }}
                />
              </div>
              <div className="flex items-center gap-2 mt-2">
                {getStatusIcon(health.memory.status)}
                <span className="text-sm capitalize">{health.memory.status}</span>
              </div>
            </div>
          </div>

          {/* Disk */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-4">
              <HardDrive className="text-green-500" size={24} />
              <div>
                <h3 className="font-semibold">Disk Usage</h3>
                <p className="text-sm text-gray-500">{health.disk.total_gb.toFixed(1)} GB total</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Used</span>
                <span className="font-medium">{health.disk.used_gb.toFixed(1)} GB ({health.disk.usage_percent.toFixed(1)}%)</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${getProgressColor(health.disk.usage_percent)}`}
                  style={{ width: `${health.disk.usage_percent}%` }}
                />
              </div>
              <div className="flex items-center gap-2 mt-2">
                {getStatusIcon(health.disk.status)}
                <span className="text-sm capitalize">{health.disk.status}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Services Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Database size={20} />
          Services Status
        </h3>
        <div className="space-y-3">
          {services.map((service, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                {getStatusIcon(service.status)}
                <div>
                  <p className="font-medium">{service.name}</p>
                  <p className="text-sm text-gray-600">{service.message}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(service.status)}`}>
                {service.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Last Updated */}
      {health && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {new Date(health.timestamp).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default SystemHealth;
