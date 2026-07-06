import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, Shield, AlertTriangle, FileText, CheckCircle } from 'lucide-react';

interface AuditLog {
  id: string;
  user_id: string;
  user_email?: string;
  user_name?: string;
  action: string;
  ip_address?: string;
  user_agent?: string;
  metadata?: any;
  created_at: string;
}

interface SecurityEvent {
  id: string;
  event_type: string;
  user_email?: string;
  user_id?: string;
  ip_address?: string;
  reason: string;
  created_at: string;
}

const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [actionTypes, setActionTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'logs' | 'security' | 'compliance'>('logs');
  
  // Filters
  const [actionFilter, setActionFilter] = useState('');
  const [userIdFilter, setUserIdFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchActionTypes();
    if (activeTab === 'logs') {
      fetchAuditLogs();
    } else if (activeTab === 'security') {
      fetchSecurityEvents();
    }
  }, [activeTab, actionFilter, userIdFilter, startDate, endDate]);

  const fetchActionTypes = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/audit/actions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setActionTypes(data);
      }
    } catch (error) {
      console.error('Failed to fetch action types:', error);
    }
  };

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      if (actionFilter) params.append('action', actionFilter);
      if (userIdFilter) params.append('user_id', userIdFilter);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/audit/logs?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSecurityEvents = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/audit/security-events?hours=168`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setSecurityEvents(data);
      }
    } catch (error) {
      console.error('Failed to fetch security events:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateComplianceReport = async () => {
    if (!startDate || !endDate) {
      alert('Please select start and end dates for the compliance report');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/admin/audit/compliance-report?start_date=${startDate}&end_date=${endDate}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        
        // Download as JSON
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `compliance-report-${data.report_id}.json`;
        a.click();
        
        alert('Compliance report generated successfully');
      }
    } catch (error) {
      console.error('Failed to generate compliance report:', error);
      alert('Failed to generate compliance report');
    }
  };

  const exportLogs = () => {
    const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString()}.json`;
    a.click();
  };

  const filteredLogs = logs.filter(log => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      log.action.toLowerCase().includes(search) ||
      log.user_email?.toLowerCase().includes(search) ||
      log.user_name?.toLowerCase().includes(search) ||
      log.ip_address?.toLowerCase().includes(search)
    );
  });

  const getActionBadgeColor = (action: string) => {
    if (action.includes('failed') || action.includes('flagged') || action.includes('rejected')) {
      return 'bg-red-100 text-red-800';
    }
    if (action.includes('login') || action.includes('signup')) {
      return 'bg-blue-100 text-blue-800';
    }
    if (action.includes('delete') || action.includes('suspend')) {
      return 'bg-orange-100 text-orange-800';
    }
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Audit Logs & Security</h2>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab('logs')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'logs'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <FileText className="inline mr-2" size={18} />
          Audit Logs
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'security'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Shield className="inline mr-2" size={18} />
          Security Events
        </button>
        <button
          onClick={() => setActiveTab('compliance')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'compliance'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <AlertTriangle className="inline mr-2" size={18} />
          Compliance Reports
        </button>
      </div>

      {/* Audit Logs Tab */}
      {activeTab === 'logs' && (
        <>
          {/* Filters */}
          <div className="mb-6 grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg"
              />
            </div>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="">All Actions</option>
              {actionTypes.map((action) => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-4 py-2 border rounded-lg"
              placeholder="Start Date"
            />
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="px-4 py-2 border rounded-lg"
              placeholder="End Date"
            />
            <button
              onClick={exportLogs}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
            >
              <Download size={18} />
              Export
            </button>
          </div>

          {/* Logs Table */}
          {loading ? (
            <div className="text-center py-8">Loading audit logs...</div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <div className="font-medium text-gray-900">{log.user_name || 'Unknown'}</div>
                          <div className="text-gray-500">{log.user_email || log.user_id}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${getActionBadgeColor(log.action)}`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {log.ip_address || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {log.metadata && Object.keys(log.metadata).length > 0 ? (
                          <details className="cursor-pointer">
                            <summary className="text-blue-600 hover:text-blue-800">View</summary>
                            <pre className="mt-2 text-xs bg-gray-50 p-2 rounded">
                              {JSON.stringify(log.metadata, null, 2)}
                            </pre>
                          </details>
                        ) : (
                          'No details'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredLogs.length === 0 && (
                <div className="text-center py-8 text-gray-500">No audit logs found</div>
              )}
            </div>
          )}
        </>
      )}

      {/* Security Events Tab */}
      {activeTab === 'security' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 bg-red-50 border-b border-red-200">
            <h3 className="font-semibold text-red-900 flex items-center gap-2">
              <AlertTriangle size={20} />
              Security Events (Last 7 Days)
            </h3>
          </div>
          {loading ? (
            <div className="text-center py-8">Loading security events...</div>
          ) : (
            <div className="divide-y divide-gray-200">
              {securityEvents.map((event) => (
                <div key={event.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          event.event_type === 'failed_login' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                        }`}>
                          {event.event_type.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(event.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-gray-900 font-medium">{event.reason}</p>
                      <div className="mt-2 text-sm text-gray-600">
                        {event.user_email && <p>Email: {event.user_email}</p>}
                        {event.ip_address && <p>IP: {event.ip_address}</p>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {securityEvents.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="mx-auto mb-2 text-green-500" size={48} />
                  <p>No security events detected</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Compliance Reports Tab */}
      {activeTab === 'compliance' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Generate Compliance Report</h3>
          <p className="text-gray-600 mb-6">
            Generate a comprehensive compliance report for a specific date range. The report includes user statistics,
            login activity, security incidents, and compliance status.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
          </div>

          <button
            onClick={generateComplianceReport}
            disabled={!startDate || !endDate}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Download size={20} />
            Generate & Download Report
          </button>

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Report Contents:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Total users and new user registrations</li>
              <li>• Login statistics (successful and failed attempts)</li>
              <li>• Content violations and security incidents</li>
              <li>• Data access and deletion requests</li>
              <li>• Overall compliance status</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditLogs;
