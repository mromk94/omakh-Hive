'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, Search, Filter, Mail, Calendar, Shield,
  CheckCircle, XCircle, Clock, MoreVertical, Download, AlertCircle
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = 'http://localhost:8001';

export default function UserManagement() {
  const [users, setUsers] = useState<any[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<any>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [searchTerm, filterStatus, users]);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setUsers(data.users || []);
        setFilteredUsers(data.users || []);
        console.log(`✅ Loaded ${data.users?.length || 0} users`);
      } else {
        toast.error('Failed to load users');
      }
      setLoading(false);
    } catch (error: any) {
      console.error('Failed to fetch users:', error);
      toast.error(`Error loading users: ${error?.message || 'Unknown error'}`);
      setLoading(false);
    }
  };

  const filterUsers = () => {
    let filtered = users;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(user => 
        user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.wallet?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(user => user.status === filterStatus);
    }

    setFilteredUsers(filtered);
  };

  if (loading) {
    return (
      <div className="text-center text-gray-400 py-12">
        <div className="w-8 h-8 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        Loading users...
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-12 text-center">
        <AlertCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">No Users Found</h3>
        <p className="text-gray-400 mb-6">
          No users have registered yet. Once users sign up, they will appear here for management.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">User Management</h3>
          <p className="text-sm text-gray-400">
            {users.length} total users • {filteredUsers.length} shown
          </p>
        </div>
        <button className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg flex items-center gap-2 text-black">
          <Download className="w-4 h-4" />
          Export Users
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatBox
          label="Total Users"
          value={users.length}
          icon={Users}
          color="blue"
        />
        <StatBox
          label="Active"
          value={users.filter(u => u.status === 'active').length}
          icon={CheckCircle}
          color="green"
        />
        <StatBox
          label="Pending"
          value={users.filter(u => u.status === 'pending').length}
          icon={Clock}
          color="yellow"
        />
        <StatBox
          label="Suspended"
          value={users.filter(u => u.status === 'suspended').length}
          icon={XCircle}
          color="red"
        />
      </div>

      {/* Search & Filter */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by email, name, or wallet..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="pending">Pending</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      {filteredUsers.length === 0 ? (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-12 text-center">
          <Users className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No users found matching your criteria</p>
        </div>
      ) : (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-800/50 border-b border-gray-700">
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">User</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Type</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Joined</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user, index) => (
                  <motion.tr
                    key={user.id || index}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-white font-medium">{user.name || user.email}</div>
                        <div className="text-sm text-gray-400">{user.email}</div>
                        {user.wallet && (
                          <div className="text-xs text-gray-500 mt-1">
                            {user.wallet.slice(0, 6)}...{user.wallet.slice(-4)}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-300 capitalize">
                        {user.user_type || 'explorer'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={user.status || 'active'} />
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-300">
                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => setSelectedUser(user)}
                        className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <MoreVertical className="w-4 h-4 text-gray-400" />
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* User Detail Modal */}
      {selectedUser && (
        <UserDetailModal
          user={selectedUser}
          onClose={() => setSelectedUser(null)}
          onUpdate={fetchUsers}
        />
      )}
    </div>
  );
}

// ==================== SUB-COMPONENTS ====================

function StatBox({ label, value, icon: Icon, color }: any) {
  const colors: any = {
    blue: 'from-blue-600/20 to-blue-700/20 border-blue-500/30',
    green: 'from-green-600/20 to-green-700/20 border-green-500/30',
    yellow: 'from-yellow-600/20 to-yellow-700/20 border-yellow-500/30',
    red: 'from-red-600/20 to-red-700/20 border-red-500/30',
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} border rounded-xl p-4`}>
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-6 h-6 text-gray-400" />
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-sm text-gray-400">{label}</div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: any = {
    active: { bg: 'bg-green-500/20', text: 'text-green-400', label: 'Active' },
    pending: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'Pending' },
    suspended: { bg: 'bg-red-500/20', text: 'text-red-400', label: 'Suspended' },
  };

  const { bg, text, label } = config[status] || config.active;

  return (
    <span className={`${bg} ${text} px-3 py-1 rounded-full text-xs font-medium`}>
      {label}
    </span>
  );
}

function UserDetailModal({ user, onClose, onUpdate }: any) {
  const [action, setAction] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAction = async (actionType: string) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('auth_token');
      await fetch(`${BACKEND_URL}/api/v1/admin/users/${user.id}/${actionType}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gray-900 border border-gray-800 rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white">User Details</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <XCircle className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-400 mb-1">Email</div>
              <div className="text-white">{user.email}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Status</div>
              <StatusBadge status={user.status || 'active'} />
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">User Type</div>
              <div className="text-white capitalize">{user.user_type || 'explorer'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Joined</div>
              <div className="text-white">
                {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </div>
            </div>
          </div>

          {user.wallet && (
            <div>
              <div className="text-sm text-gray-400 mb-1">Wallet Address</div>
              <div className="text-white font-mono text-sm bg-gray-800 p-3 rounded-lg">
                {user.wallet}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="border-t border-gray-800 pt-4 mt-6">
            <div className="text-sm font-semibold text-white mb-3">Admin Actions</div>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleAction('suspend')}
                disabled={loading}
                className="px-4 py-2 bg-red-600/20 text-red-400 hover:bg-red-600/30 rounded-lg transition-colors disabled:opacity-50"
              >
                Suspend User
              </button>
              <button
                onClick={() => handleAction('activate')}
                disabled={loading}
                className="px-4 py-2 bg-green-600/20 text-green-400 hover:bg-green-600/30 rounded-lg transition-colors disabled:opacity-50"
              >
                Activate User
              </button>
              <button
                onClick={() => handleAction('reset-password')}
                disabled={loading}
                className="px-4 py-2 bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 rounded-lg transition-colors disabled:opacity-50"
              >
                Reset Password
              </button>
              <button
                onClick={() => handleAction('send-email')}
                disabled={loading}
                className="px-4 py-2 bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 rounded-lg transition-colors disabled:opacity-50"
              >
                Send Email
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
