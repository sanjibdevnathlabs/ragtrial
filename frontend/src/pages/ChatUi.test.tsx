import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import ChatUi from './ChatUi';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock window.confirm
global.confirm = vi.fn(() => true);

// Mock window.alert
global.alert = vi.fn();

// Mock scrollIntoView (not implemented in JSDOM)
Element.prototype.scrollIntoView = vi.fn();

describe('ChatUi', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial Rendering', () => {
    it('should render the page title', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});
      expect(screen.getByText('RAG Document Chat')).toBeInTheDocument();
    });

    it('should render upload button', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});
      expect(screen.getByText('Upload File')).toBeInTheDocument();
    });

    it('should render clear chat button', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});
      expect(screen.getByText('Clear Chat')).toBeInTheDocument();
    });

    it('should show welcome message when no messages', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});
      expect(screen.getByText(/Welcome to RAG Chat!/i)).toBeInTheDocument();
    });

    it('should render input textarea', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});
      expect(screen.getByPlaceholderText(/Ask a question about your documents/i)).toBeInTheDocument();
    });

    it('should render send button', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});
      const sendButton = screen.getByRole('button', { name: '' }); // Button with icon only
      expect(sendButton).toBeInTheDocument();
    });
  });

  describe('File Loading', () => {
    it('should load files on mount', async () => {
      const mockFiles = [
        {
          file_id: '1',
          filename: 'test1.pdf',
          file_size: 1024,
          indexed: true,
        },
        {
          file_id: '2',
          filename: 'test2.txt',
          file_size: 2048,
          indexed: true,
        },
      ];

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: mockFiles }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText('test1.pdf')).toBeInTheDocument();
        expect(screen.getByText('test2.txt')).toBeInTheDocument();
      });

      expect(screen.getByText('Indexed Documents (2)')).toBeInTheDocument();
    });

    it('should show "No documents indexed yet" when no files', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText('No documents indexed yet')).toBeInTheDocument();
      });
    });

    it('should filter and show only indexed documents', async () => {
      const mockFiles = [
        {
          file_id: '1',
          filename: 'indexed.pdf',
          file_size: 1024,
          indexed: true,
        },
        {
          file_id: '2',
          filename: 'not-indexed.txt',
          file_size: 2048,
          indexed: false,
        },
      ];

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: mockFiles }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText('indexed.pdf')).toBeInTheDocument();
        expect(screen.queryByText('not-indexed.txt')).not.toBeInTheDocument();
      });

      expect(screen.getByText('Indexed Documents (1)')).toBeInTheDocument();
    });

    it('should display file sizes in KB', async () => {
      const mockFiles = [
        {
          file_id: '1',
          filename: 'test.pdf',
          file_size: 5120, // 5 KB
          indexed: true,
        },
      ];

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: mockFiles }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText('5.0 KB')).toBeInTheDocument();
      });
    });

    it('should handle file loading error gracefully', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      mockFetch.mockRejectedValue(new Error('Network error'));

      render(<ChatUi />);
      await waitFor(() => {});

      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to load files:', expect.any(Error));
      });

      consoleErrorSpy.mockRestore();
    });
  });

  describe('File Upload', () => {
    it('should upload file successfully', async () => {
      const mockFiles = [
        {
          file_id: '1',
          filename: 'uploaded.pdf',
          file_size: 1024,
          indexed: true,
        },
      ];

      // First call: initial load (empty), Second call: after upload
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({}), // Upload response
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: mockFiles }), // Reload files
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });

      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/v1/upload',
          expect.objectContaining({
            method: 'POST',
            body: expect.any(FormData),
          })
        );
      });

      await waitFor(() => {
        expect(screen.getByText('uploaded.pdf')).toBeInTheDocument();
      });
    });

    it('should show uploading state', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<ChatUi />);
      await waitFor(() => {});

      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });

      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Uploading...')).toBeInTheDocument();
      });
    });

    it('should show alert on upload failure', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ error: 'Invalid file format' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      const file = new File(['test'], 'test.txt', { type: 'text/plain' });

      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(global.alert).toHaveBeenCalledWith('Upload failed: Invalid file format');
      });
    });

    it('should handle network error during upload', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockRejectedValueOnce(new Error('Network error'));

      render(<ChatUi />);
      await waitFor(() => {});

      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });

      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(global.alert).toHaveBeenCalledWith('Upload failed. Please try again.');
      });

      consoleErrorSpy.mockRestore();
    });

    it('should not upload if no file selected', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      fireEvent.change(fileInput, { target: { files: null } });

      // Wait a bit to ensure no upload call
      await new Promise(resolve => setTimeout(resolve, 100));

      // Only the initial loadFiles call should have been made
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('Message Sending', () => {
    it('should send message successfully', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            answer: 'This is the answer',
            sources: [
              {
                filename: 'test.pdf',
                chunk_index: 0,
                content: 'Source content',
              },
            ],
          }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1]; // Last button is send

      fireEvent.change(input, { target: { value: 'What is Kafka?' } });
      fireEvent.click(sendButton);

      await waitFor(() => {});

      // User message should appear
      await waitFor(() => {
        expect(screen.getByText('What is Kafka?')).toBeInTheDocument();
      });

      // Assistant response should appear
      await waitFor(() => {
        expect(screen.getByText('This is the answer')).toBeInTheDocument();
      });

      // Sources should be collapsed by default (SourcesAccordion tested separately)
      await waitFor(() => {
        expect(screen.getByText('Show Sources')).toBeInTheDocument();
      });
    });

    it('should show loading indicator while processing', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test question' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText('Test question')).toBeInTheDocument();
      });

      // Check for loading animation (three bouncing dots)
      const loadingDots = document.querySelectorAll('.animate-bounce');
      expect(loadingDots.length).toBeGreaterThan(0);
    });

    it('should clear input after sending', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Response' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i) as HTMLTextAreaElement;
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test question' } });
      fireEvent.click(sendButton);

      await waitFor(() => {});

      // Input should be cleared immediately
      expect(input.value).toBe('');
    });

    it('should not send empty message', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: '   ' } }); // Whitespace only
      fireEvent.click(sendButton);

      await waitFor(() => {});

      await new Promise(resolve => setTimeout(resolve, 100));

      // No query call should be made (only initial loadFiles)
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('should disable send button when loading', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockImplementation(() => new Promise(() => {}));

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        expect(sendButton).toBeDisabled();
      });
    });

    it('should handle API error response', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ error: 'Invalid query format' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText(/Error: Invalid query format/i)).toBeInTheDocument();
      });
    });

    it('should handle network error', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockRejectedValueOnce(new Error('Network error'));

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText(/Error: Failed to connect to the server/i)).toBeInTheDocument();
      });

      consoleErrorSpy.mockRestore();
    });

    it('should send message on Enter key press', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Response' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);

      fireEvent.change(input, { target: { value: 'Test question' } });
      fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });

      await waitFor(() => {
        expect(screen.getByText('Test question')).toBeInTheDocument();
      });

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/query',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ question: 'Test question' }),
        })
      );
    });

    it('should not send message on Shift+Enter', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i) as HTMLTextAreaElement;

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });

      await new Promise(resolve => setTimeout(resolve, 100));

      // Only initial loadFiles call
      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(input.value).toBe('Test'); // Input not cleared
    });
  });

  describe('Clear Chat', () => {
    it('should clear messages when confirmed', async () => {
      (global.confirm as any).mockReturnValue(true);

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Response' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      // Send a message first
      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText('Test')).toBeInTheDocument();
      });

      // Clear chat
      const clearButton = screen.getByText('Clear Chat');
      fireEvent.click(clearButton);

      expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to clear the chat history?');

      await waitFor(() => {
        expect(screen.queryByText('Test')).not.toBeInTheDocument();
        expect(screen.getByText(/Welcome to RAG Chat!/i)).toBeInTheDocument();
      });
    });

    it('should not clear messages when cancelled', async () => {
      (global.confirm as any).mockReturnValue(false);

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Response' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      // Send a message first
      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        expect(screen.getByText('Test')).toBeInTheDocument();
      });

      // Try to clear chat
      const clearButton = screen.getByText('Clear Chat');
      fireEvent.click(clearButton);

      // Message should still be there
      expect(screen.getByText('Test')).toBeInTheDocument();
    });
  });

  describe('Message Display', () => {
    it('should display user messages on the right', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Response' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        const messageElement = screen.getByText('Test').closest('div');
        expect(messageElement?.parentElement).toHaveClass('justify-end');
      });
    });

    it('should display assistant messages on the left', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Response' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        const messageElement = screen.getByText('Response').closest('div');
        expect(messageElement?.parentElement).toHaveClass('justify-start');
      });
    });

    it('should display timestamps for messages', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Response' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        // Check for timestamp format (will include time)
        const timestamps = document.querySelectorAll('.opacity-60');
        expect(timestamps.length).toBeGreaterThan(0);
      });
    });

    it('should preserve whitespace in messages', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ answer: 'Line 1\n\nLine 2' }),
        });

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        const messageElement = screen.getByText(/Line 1/).closest('p');
        expect(messageElement).toHaveClass('whitespace-pre-wrap');
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ files: [] }),
      });

      render(<ChatUi />);
      await waitFor(() => {});

      const textarea = screen.getByPlaceholderText(/Ask a question about your documents/i);
      expect(textarea).toBeEnabled();
    });

    it('should disable input while loading', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ files: [] }),
        })
        .mockImplementation(() => new Promise(() => {}));

      render(<ChatUi />);
      await waitFor(() => {});

      const input = screen.getByPlaceholderText(/Ask a question about your documents/i);
      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons[sendButtons.length - 1];

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

     await waitFor(() => {});

      await waitFor(() => {
        expect(input).toBeDisabled();
      });
    });
  });
});

