import { useState, useEffect } from 'react';
import DataTable, { Column } from '../../components/admin/DataTable';
import Modal from '../../components/admin/Modal';
import { TextInput, TextareaInput, FormButtons } from '../../components/admin/FormComponents';

interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
  description: string | null;
  created_at: number;
  updated_at: number;
}

export default function Permissions() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Permission | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    resource: '',
    action: '',
    description: '',
  });

  useEffect(() => {
    fetchPermissions();
  }, []);

  const fetchPermissions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/permissions', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setPermissions(data);
      }
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({ name: '', resource: '', action: '', description: '' });
    setIsModalOpen(true);
  };

  const handleEdit = (item: Permission) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      resource: item.resource,
      action: item.action,
      description: item.description || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    const url = editingItem ? `/admin/permissions/${editingItem.id}` : '/admin/permissions';
    const method = editingItem ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setIsModalOpen(false);
        fetchPermissions();
      }
    } catch (error) {
      console.error('Failed to save permission:', error);
    }
  };

  const handleDelete = async (item: Permission) => {
    if (!confirm(`Delete permission "${item.name}"?`)) return;

    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(`/admin/permissions/${item.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchPermissions();
      }
    } catch (error) {
      console.error('Failed to delete permission:', error);
    }
  };

  const columns: Column<Permission>[] = [
    { key: 'name', label: 'Permission Name' },
    { key: 'resource', label: 'Resource' },
    { key: 'action', label: 'Action' },
    { key: 'description', label: 'Description', render: (value) => value || '-' },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Permissions</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage system permissions and access control</p>
        </div>
        <button
          onClick={handleCreate}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <span className="mr-2">➕</span>
          Create Permission
        </button>
      </div>

      <DataTable
        columns={columns}
        data={permissions}
        onEdit={handleEdit}
        onDelete={handleDelete}
        loading={loading}
        emptyMessage="No permissions found"
      />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingItem ? 'Edit Permission' : 'Create Permission'}>
        <form onSubmit={handleSubmit}>
          <TextInput
            label="Permission Name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., user:read, file:delete"
            maxLength={100}
          />

          <TextInput
            label="Resource"
            required
            value={formData.resource}
            onChange={(e) => setFormData({ ...formData, resource: e.target.value })}
            placeholder="e.g., user, file, role"
            maxLength={50}
          />

          <TextInput
            label="Action"
            required
            value={formData.action}
            onChange={(e) => setFormData({ ...formData, action: e.target.value })}
            placeholder="e.g., read, write, delete, update"
            maxLength={50}
          />

          <TextareaInput
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            placeholder="Optional description of what this permission allows"
            maxLength={500}
          />

          <FormButtons onCancel={() => setIsModalOpen(false)} />
        </form>
      </Modal>
    </div>
  );
}

