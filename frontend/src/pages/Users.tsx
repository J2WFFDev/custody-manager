import React, { useState, useEffect } from 'react';
import { getRoleBadgeColor, VALID_ROLES } from '../utils';

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  verified_adult: boolean;
  is_active: boolean;
  created_at: string;
}

const Users: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call when backend is connected
      // const response = await fetch('/api/v1/users', {
      //   headers: {
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   }
      // });
      // const data = await response.json();
      // setUsers(data);
      
      // Mock data for demonstration
      const mockUsers: User[] = [
        {
          id: 1,
          email: 'admin@example.com',
          name: 'Admin User',
          role: 'admin',
          verified_adult: true,
          is_active: true,
          created_at: '2024-01-15T10:00:00Z'
        },
        {
          id: 2,
          email: 'armorer@example.com',
          name: 'John Armorer',
          role: 'armorer',
          verified_adult: true,
          is_active: true,
          created_at: '2024-01-16T10:00:00Z'
        },
        {
          id: 3,
          email: 'coach@example.com',
          name: 'Jane Coach',
          role: 'coach',
          verified_adult: true,
          is_active: true,
          created_at: '2024-01-17T10:00:00Z'
        },
        {
          id: 4,
          email: 'parent@example.com',
          name: 'Parent User',
          role: 'parent',
          verified_adult: false,
          is_active: true,
          created_at: '2024-01-18T10:00:00Z'
        }
      ];
      setUsers(mockUsers);
      setError(null);
    } catch (err) {
      setError('Failed to load users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      // TODO: Replace with actual API call when backend is connected
      // await fetch(`/api/v1/users/${userId}`, {
      //   method: 'PATCH',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({ role: newRole })
      // });
      
      // Update local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, role: newRole } : user
      ));
    } catch (err) {
      console.error('Error updating role:', err);
      alert('Failed to update user role');
    }
  };

  const handleVerifiedAdultToggle = async (userId: number, newValue: boolean) => {
    try {
      // TODO: Replace with actual API call when backend is connected
      // await fetch(`/api/v1/users/${userId}`, {
      //   method: 'PATCH',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({ verified_adult: newValue })
      // });
      
      // Update local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, verified_adult: newValue } : user
      ));
    } catch (err) {
      console.error('Error updating verified adult status:', err);
      alert('Failed to update verified adult status');
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-12">
          <div className="text-gray-600">Loading users...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">User Management</h1>
        <p className="text-gray-600">
          Manage user roles and verified adult status (Admin only)
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Verified Adult
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Joined
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {user.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {user.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {VALID_ROLES.map((role) => (
                        <option key={role} value={role}>
                          {role.charAt(0).toUpperCase() + role.slice(1)}
                        </option>
                      ))}
                    </select>
                    <span className={`ml-2 px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={user.verified_adult}
                        onChange={(e) => handleVerifiedAdultToggle(user.id, e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {user.verified_adult ? (
                          <span className="text-green-600 font-medium">✓ Verified</span>
                        ) : (
                          <span className="text-gray-500">Not Verified</span>
                        )}
                      </span>
                    </label>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-6 bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-600" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              <span className="font-semibold">Role Assignment:</span> Admin can assign roles (Armorer, Coach, Volunteer, Parent) to control access.
              <br />
              <span className="font-semibold">Verified Adult Flag:</span> Only verified adults can accept off-site custody responsibility.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Users;
