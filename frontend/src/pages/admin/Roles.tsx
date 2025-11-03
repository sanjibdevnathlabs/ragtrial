import { useState, useEffect } from 'react';
import DataTable, { Column } from '../../components/admin/DataTable';
import Modal from '../../components/admin/Modal';
import { TextInput, TextareaInput, FormButtons } from '../../components/admin/FormComponents';

interface Role {
  id: string;
  name: string;
  description: string | null;
  created_at: number;
  updated_at: number;
}

export default function Roles() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Role | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/roles', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setRoles(data);
      }
    } catch (error) {
      console.error('Failed to fetch roles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({ name: '', description: '' });
    setIsModalOpen(true);
  };

  const handleEdit = (item: Role) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      description: item.description || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    const url = editingItem ? `/admin/roles/${editingItem.id}` : '/admin/roles';
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
        fetchRoles();
      }
    } catch (error) {
      console.error('Failed to save role:', error);
    }
  };

  const handleDelete = async (item: Role) => {
    if (!confirm(`Delete role "${item.name}"?`)) return;

    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(`/admin/roles/${item.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchRoles();
      }
    } catch (error) {
      console.error('Failed to delete role:', error);
    }
  };

  const columns: Column<Role>[] = [
    { key: 'name', label: 'Role Name' },
    { key: 'description', label: 'Description', render: (value) => value || '-' },
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Roles</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage user roles and their permissions</p>
        </div>
        <button
          onClick={handleCreate}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <span className="mr-2">➕</span>
          Create Role
        </button>
      </div>

      <DataTable
        columns={columns}
        data={roles}
        onEdit={handleEdit}
        onDelete={handleDelete}
        loading={loading}
        emptyMessage="No roles found"
      />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingItem ? 'Edit Role' : 'Create Role'}>
        <form onSubmit={handleSubmit}>
          <TextInput
            label="Role Name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., editor, moderator"
            maxLength={50}
          />

          <TextareaInput
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            placeholder="Optional description of this role's purpose"
            maxLength={500}
          />

          <FormButtons onCancel={() => setIsModalOpen(false)} />
        </form>
      </Modal>
    </div>
  );
}

