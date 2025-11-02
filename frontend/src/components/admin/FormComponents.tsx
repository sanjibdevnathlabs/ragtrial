import { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react';

interface FormFieldProps {
  label: string;
  error?: string;
  required?: boolean;
}

// Text Input
interface TextInputProps extends InputHTMLAttributes<HTMLInputElement>, FormFieldProps {}

export function TextInput({ label, error, required, ...props }: TextInputProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <input
        {...props}
        className={`w-full px-4 py-2 rounded-lg border ${
          error
            ? 'border-red-500 focus:ring-red-500'
            : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500'
        } bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:border-transparent transition-colors`}
      />
      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}

// Textarea
interface TextareaInputProps extends TextareaHTMLAttributes<HTMLTextAreaElement>, FormFieldProps {}

export function TextareaInput({ label, error, required, ...props }: TextareaInputProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <textarea
        {...props}
        className={`w-full px-4 py-2 rounded-lg border ${
          error
            ? 'border-red-500 focus:ring-red-500'
            : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500'
        } bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:border-transparent transition-colors`}
      />
      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}

// Select
interface SelectInputProps extends SelectHTMLAttributes<HTMLSelectElement>, FormFieldProps {
  options: { value: string; label: string }[];
}

export function SelectInput({ label, error, required, options, ...props }: SelectInputProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <select
        {...props}
        className={`w-full px-4 py-2 rounded-lg border ${
          error
            ? 'border-red-500 focus:ring-red-500'
            : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500'
        } bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:border-transparent transition-colors`}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}

// Checkbox
interface CheckboxInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function CheckboxInput({ label, ...props }: CheckboxInputProps) {
  return (
    <div className="mb-4 flex items-center">
      <input
        type="checkbox"
        {...props}
        className="w-4 h-4 text-blue-600 bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
      />
      <label className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>
    </div>
  );
}

// Form Buttons
export function FormButtons({
  onCancel,
  submitText = 'Save',
  cancelText = 'Cancel',
  loading = false,
}: {
  onCancel: () => void;
  submitText?: string;
  cancelText?: string;
  loading?: boolean;
}) {
  return (
    <div className="flex justify-end space-x-3 mt-6">
      <button
        type="button"
        onClick={onCancel}
        disabled={loading}
        className="px-6 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
      >
        {cancelText}
      </button>
      <button
        type="submit"
        disabled={loading}
        className="px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
      >
        {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>}
        {submitText}
      </button>
    </div>
  );
}

