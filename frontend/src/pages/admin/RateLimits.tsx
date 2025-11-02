import { useState, useEffect } from 'react';
import DataTable, { Column } from '../../components/admin/DataTable';
import Modal from '../../components/admin/Modal';
import { TextInput, TextareaInput, SelectInput, CheckboxInput, FormButtons } from '../../components/admin/FormComponents';

interface RateLimit {
  id: string;
  route_name: string;
  requests: number;
  window_seconds: number;
  enabled: boolean;
  key_strategy: string;
  description: string | null;
  created_at: number;
  updated_at: number;
}

export default function RateLimits() {
  const [rateLimits, setRateLimits] = useState<RateLimit[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<RateLimit | null>(null);
  const [formData, setFormData] = useState({
    route_name: '',
    requests: 100,
    window_seconds: 60,
    enabled: true,
    key_strategy: 'ip',
    description: '',
  });

  useEffect(() => {
    fetchRateLimits();
  }, []);

  const fetchRateLimits = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/rate-limits', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setRateLimits(data);
      }
    } catch (error) {
      console.error('Failed to fetch rate limits:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({
      route_name: '',
      requests: 100,
      window_seconds: 60,
      enabled: true,
      key_strategy: 'ip',
      description: '',
    });
    setIsModalOpen(true);
  };

  const handleEdit = (item: RateLimit) => {
    setEditingItem(item);
    setFormData({
      route_name: item.route_name,
      requests: item.requests,
      window_seconds: item.window_seconds,
      enabled: item.enabled,
      key_strategy: item.key_strategy,
      description: item.description || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    const url = editingItem
      ? `/api/v1/admin/rate-limits/${editingItem.route_name}`
      : '/api/v1/admin/rate-limits';
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
        fetchRateLimits();
      }
    } catch (error) {
      console.error('Failed to save rate limit:', error);
    }
  };

  const handleDelete = async (item: RateLimit) => {
    if (!confirm(`Delete rate limit for "${item.route_name}"?`)) return;

    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(`/api/v1/admin/rate-limits/${item.route_name}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchRateLimits();
      }
    } catch (error) {
      console.error('Failed to delete rate limit:', error);
    }
  };

  const columns: Column<RateLimit>[] = [
    { key: 'route_name', label: 'Route Name' },
    { key: 'requests', label: 'Requests' },
    { key: 'window_seconds', label: 'Window (s)' },
    { key: 'key_strategy', label: 'Strategy' },
    {
      key: 'enabled',
      label: 'Status',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${value ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}>
          {value ? 'Enabled' : 'Disabled'}
        </span>
      ),
    },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Rate Limits</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage API rate limiting configurations</p>
        </div>
        <button
          onClick={handleCreate}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <span className="mr-2">➕</span>
          Create Rate Limit
        </button>
      </div>

      <DataTable
        columns={columns}
        data={rateLimits}
        onEdit={handleEdit}
        onDelete={handleDelete}
        loading={loading}
        emptyMessage="No rate limits configured"
      />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingItem ? 'Edit Rate Limit' : 'Create Rate Limit'}>
        <form onSubmit={handleSubmit}>
          <TextInput
            label="Route Name"
            required
            value={formData.route_name}
            onChange={(e) => setFormData({ ...formData, route_name: e.target.value })}
            placeholder="e.g., global, auth_login, admin_users"
            disabled={!!editingItem}
          />

          <TextInput
            label="Requests Limit"
            type="number"
            required
            value={formData.requests}
            onChange={(e) => setFormData({ ...formData, requests: parseInt(e.target.value) })}
            min={1}
          />

          <TextInput
            label="Time Window (seconds)"
            type="number"
            required
            value={formData.window_seconds}
            onChange={(e) => setFormData({ ...formData, window_seconds: parseInt(e.target.value) })}
            min={1}
          />

          <SelectInput
            label="Key Strategy"
            required
            value={formData.key_strategy}
            onChange={(e) => setFormData({ ...formData, key_strategy: e.target.value })}
            options={[
              { value: 'ip', label: 'IP Address' },
              { value: 'user', label: 'User ID' },
              { value: 'session', label: 'Session ID' },
              { value: 'route', label: 'Route' },
              { value: 'ip_and_route', label: 'IP + Route' },
              { value: 'user_and_route', label: 'User + Route' },
            ]}
          />

          <TextareaInput
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            placeholder="Optional description for this rate limit"
          />

          <CheckboxInput
            label="Enabled"
            checked={formData.enabled}
            onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
          />

          <FormButtons onCancel={() => setIsModalOpen(false)} />
        </form>
      </Modal>
    </div>
  );
}

