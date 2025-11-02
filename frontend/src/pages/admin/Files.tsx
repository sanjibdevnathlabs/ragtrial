import { useState, useEffect } from 'react';
import DataTable, { Column } from '../../components/admin/DataTable';

interface File {
  id: string;
  filename: string;
  file_size: number;
  file_type: string;
  indexed: boolean;
  indexed_at: number | null;
  created_at: number;
  user_id: string;
}

export default function Files() {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/files', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }
    } catch (error) {
      console.error('Failed to fetch files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (item: File) => {
    if (!confirm(`Delete file "${item.filename}"?`)) return;

    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(`/api/v1/files/${item.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchFiles();
      }
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const columns: Column<File>[] = [
    { key: 'filename', label: 'Filename' },
    { key: 'file_type', label: 'Type' },
    {
      key: 'file_size',
      label: 'Size',
      render: (value) => formatFileSize(value),
    },
    {
      key: 'indexed',
      label: 'Status',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${value ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'}`}>
          {value ? 'Indexed' : 'Not Indexed'}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Uploaded',
      render: (value) => new Date(value).toLocaleDateString(),
    },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Files</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage uploaded files and documents</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={fetchFiles}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center"
          >
            <span className="mr-2">🔄</span>
            Refresh
          </button>
          <a
            href="/api/v1/upload"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <span className="mr-2">⬆️</span>
            Upload File
          </a>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Files</h3>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{files.length}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Indexed</h3>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400">
            {files.filter((f) => f.indexed).length}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Not Indexed</h3>
          <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
            {files.filter((f) => !f.indexed).length}
          </p>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={files}
        onDelete={handleDelete}
        loading={loading}
        emptyMessage="No files uploaded yet"
      />
    </div>
  );
}

