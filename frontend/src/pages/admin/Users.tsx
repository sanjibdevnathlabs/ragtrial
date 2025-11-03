import { useState, useEffect } from 'react';
import DataTable, { Column } from '../../components/admin/DataTable';
import Modal from '../../components/admin/Modal';
import { TextInput, SelectInput, FormButtons } from '../../components/admin/FormComponents';

interface User {
  id: string;
  email: string;
  full_name: string;
  status: string;
  is_verified: boolean;
  email_verified_at: number | null;
  created_at: number;
  updated_at: number;
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<User | null>(null);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    status: 'active',
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/users', {
        headers: { Authorization: `Bearer ${token}` },
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

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({
      email: '',
      full_name: '',
      password: '',
      status: 'active',
    });
    setIsModalOpen(true);
  };

  const handleEdit = (item: User) => {
    setEditingItem(item);
    setFormData({
      email: item.email,
      full_name: item.full_name,
      password: '',
      status: item.status,
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    const url = editingItem ? `/admin/users/${editingItem.id}` : '/admin/users';
    const method = editingItem ? 'PUT' : 'POST';

    const payload = editingItem
      ? { full_name: formData.full_name, status: formData.status }
      : formData;

    try {
      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setIsModalOpen(false);
        fetchUsers();
      }
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  };

  const handleDelete = async (item: User) => {
    if (!confirm(`Delete user "${item.email}"?`)) return;

    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(`/api/v1/admin/users/${item.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchUsers();
      }
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  const columns: Column<User>[] = [
    { key: 'email', label: 'Email' },
    { key: 'full_name', label: 'Full Name' },
    {
      key: 'status',
      label: 'Status',
      render: (value) => {
        const colors = {
          active: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
          inactive: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400',
          suspended: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
        };
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[value as keyof typeof colors] || colors.inactive}`}>
            {value}
          </span>
        );
      },
    },
    {
      key: 'is_verified',
      label: 'Verified',
      render: (value) => (
        <span>{value ? '✅' : '❌'}</span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (value) => new Date(value).toLocaleDateString(),
    },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Users</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage user accounts and permissions</p>
        </div>
        <button
          onClick={handleCreate}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <span className="mr-2">➕</span>
          Create User
        </button>
      </div>

      <DataTable
        columns={columns}
        data={users}
        onEdit={handleEdit}
        onDelete={handleDelete}
        loading={loading}
        emptyMessage="No users found"
      />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingItem ? 'Edit User' : 'Create User'}>
        <form onSubmit={handleSubmit}>
          <TextInput
            label="Email"
            type="email"
            required
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="user@example.com"
            disabled={!!editingItem}
          />

          <TextInput
            label="Full Name"
            required
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            placeholder="John Doe"
          />

          {!editingItem && (
            <TextInput
              label="Password"
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Minimum 8 characters"
              minLength={8}
            />
          )}

          <SelectInput
            label="Status"
            required
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            options={[
              { value: 'active', label: 'Active' },
              { value: 'inactive', label: 'Inactive' },
              { value: 'suspended', label: 'Suspended' },
            ]}
          />

          <FormButtons onCancel={() => setIsModalOpen(false)} />
        </form>
      </Modal>
    </div>
  );
}

