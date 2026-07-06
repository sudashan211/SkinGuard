import React, { useState, useEffect } from 'react';
import { Search, UserX, Download, Trash2, AlertCircle, CheckCircle } from 'lucide-react';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  verified: boolean;
  last_login?: string;
  created_at: string;
  total_screenings?: number;
  total_appointments?: number;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, [searchTerm, roleFilter]);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (roleFilter) params.append('role', roleFilter);

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewUserDetails = async (userId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedUser(data);
        setShowDetails(true);
      }
    } catch (error) {
      console.error('Failed to fetch user details:', error);
    }
  };

  const suspendUser = async (userId: string) => {
    const reason = prompt('Enter reason for suspension:');
    if (!reason) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${userId}/suspend?reason=${encodeURIComponent(reason)}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('User suspended successfully');
        fetchUsers();
      }
    } catch (error) {
      console.error('Failed to suspend user:', error);
    }
  };

  const exportUserData = async (userId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${userId}/export`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `user-${userId}-export.json`;
        a.click();
      }
    } catch (error) {
      console.error('Failed to export user data:', error);
    }
  };

  const deleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to permanently delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('User deleted successfully');
        fetchUsers();
      }
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">User Management</h2>

      {/* Search and Filters */}
      <div className="mb-6 flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="">All Roles</option>
          <option value="patient">Patients</option>
          <option value="doctor">Doctors</option>
          <option value="admin">Admins</option>
        </select>
      </div>

      {/* Users Table */}
      {loading ? (
        <div className="text-center py-8">Loading users...</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Login</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-medium text-gray-900">{user.full_name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                      user.role === 'doctor' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`flex items-center gap-1 text-sm ${
                      user.status === 'active' ? 'text-green-600' :
                      user.status === 'suspended' ? 'text-red-600' :
                      'text-gray-600'
                    }`}>
                      {user.status === 'active' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => viewUserDetails(user.id)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        View
                      </button>
                      {user.status === 'active' && (
                        <button
                          onClick={() => suspendUser(user.id)}
                          className="text-orange-600 hover:text-orange-800 text-sm flex items-center gap-1"
                        >
                          <UserX size={14} /> Suspend
                        </button>
                      )}
                      <button
                        onClick={() => exportUserData(user.id)}
                        className="text-green-600 hover:text-green-800 text-sm flex items-center gap-1"
                      >
                        <Download size={14} /> Export
                      </button>
                      <button
                        onClick={() => deleteUser(user.id)}
                        className="text-red-600 hover:text-red-800 text-sm flex items-center gap-1"
                      >
                        <Trash2 size={14} /> Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* User Details Modal */}
      {showDetails && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">User Details</h3>
            <div className="space-y-4">
              <div>
                <label className="font-semibold">Name:</label>
                <p>{selectedUser.full_name}</p>
              </div>
              <div>
                <label className="font-semibold">Email:</label>
                <p>{selectedUser.email}</p>
              </div>
              <div>
                <label className="font-semibold">Role:</label>
                <p>{selectedUser.role}</p>
              </div>
              <div>
                <label className="font-semibold">Status:</label>
                <p>{selectedUser.status}</p>
              </div>
              <div>
                <label className="font-semibold">Verified:</label>
                <p>{selectedUser.verified ? 'Yes' : 'No'}</p>
              </div>
              <div>
                <label className="font-semibold">Member Since:</label>
                <p>{new Date(selectedUser.created_at).toLocaleDateString()}</p>
              </div>
              {selectedUser.total_screenings !== undefined && (
                <div>
                  <label className="font-semibold">Total Screenings:</label>
                  <p>{selectedUser.total_screenings}</p>
                </div>
              )}
              {selectedUser.total_appointments !== undefined && (
                <div>
                  <label className="font-semibold">Total Appointments:</label>
                  <p>{selectedUser.total_appointments}</p>
                </div>
              )}
            </div>
            <button
              onClick={() => setShowDetails(false)}
              className="mt-6 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
