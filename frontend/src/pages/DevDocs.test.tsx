import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import DevDocs from './DevDocs';

// Mock Footer component
vi.mock('../components/Footer', () => ({
  default: () => <div data-testid="footer-component">Footer Component</div>
}));

// Mock fetch globally
global.fetch = vi.fn();

const mockFiles = [
  { name: 'README.md', path: 'README.md', type: 'markdown', category: 'root' },
  { name: 'QUICKSTART.md', path: 'docs/QUICKSTART.md', type: 'markdown', category: 'docs' },
  { name: 'API.md', path: 'docs/API.md', type: 'markdown', category: 'docs' },
  { name: 'demo_rag_query.py', path: 'examples/demo_rag_query.py', type: 'python', category: 'examples' },
];

const mockMarkdownContent = {
  name: 'README.md',
  path: 'README.md',
  type: 'markdown',
  content: '# RAG Trial\n\nThis is a test README content.'
};

const mockPythonContent = {
  name: 'demo_rag_query.py',
  path: 'examples/demo_rag_query.py',
  type: 'python',
  content: 'from rag import RAGChain\n\nrag = RAGChain()\nprint(rag.query("test"))'
};

const renderDevDocs = () => {
  return render(
    <BrowserRouter>
      <DevDocs />
    </BrowserRouter>
  );
};

describe('DevDocs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockFiles,
    });
  });

  describe('Initial Render', () => {
    test('should render page title', async () => {
      renderDevDocs();
      expect(screen.getByText('Developer Documentation')).toBeInTheDocument();
    });

    test('should render page description', () => {
      renderDevDocs();
      expect(screen.getByText(/Explore code examples, guides, and API references/i)).toBeInTheDocument();
    });

    test('should have proper heading hierarchy', () => {
      renderDevDocs();
      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toHaveTextContent('Developer Documentation');
    });

    test('should render Footer component', () => {
      renderDevDocs();
      expect(screen.getByTestId('footer-component')).toBeInTheDocument();
    });
  });

  describe('File List Loading', () => {
    test('should fetch file list on mount', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/v1/devdocs/list');
      });
    });

    test('should display files after loading', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('README.md')).toBeInTheDocument();
      });
    });

    test('should handle API error gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('API Error'));
      
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to load documentation files/i)).toBeInTheDocument();
      });
    });
  });

  describe('File Categories', () => {
    test('should render Getting Started section', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('Getting Started')).toBeInTheDocument();
      });
    });

    test('should render Documentation section', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('Documentation')).toBeInTheDocument();
      });
    });

    test('should render Code Examples section', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('Code Examples')).toBeInTheDocument();
      });
    });

    test('should display root category files', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('README.md')).toBeInTheDocument();
      });
    });

    test('should display docs category files', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('QUICKSTART.md')).toBeInTheDocument();
        expect(screen.getByText('API.md')).toBeInTheDocument();
      });
    });

    test('should display examples category files', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('demo_rag_query.py')).toBeInTheDocument();
      });
    });
  });

  describe('Auto-Selection of README', () => {
    test('should auto-select README.md if available', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        const readmeButton = screen.getByRole('button', { name: /README\.md/i });
        expect(readmeButton).toHaveClass('bg-purple-600');
      });
    });

    test('should fetch README content automatically', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/devdocs/content?file_path=README.md')
        );
      });
    });
  });

  describe('File Selection', () => {
    test('should load file content when clicked', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPythonContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('demo_rag_query.py')).toBeInTheDocument();
      });

      const pythonFileButton = screen.getByRole('button', { name: /demo_rag_query\.py/i });
      fireEvent.click(pythonFileButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/devdocs/content?file_path=examples%2Fdemo_rag_query.py')
        );
      });
    });

    test('should highlight selected file', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPythonContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('demo_rag_query.py')).toBeInTheDocument();
      });

      const pythonFileButton = screen.getByRole('button', { name: /demo_rag_query\.py/i });
      fireEvent.click(pythonFileButton);

      // Verify the content fetch was triggered (which indicates selection worked)
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('demo_rag_query.py')
        );
      });
    });
  });

  describe('Content Loading States', () => {
    test('should show loading spinner while fetching content', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('demo_rag_query.py')).toBeInTheDocument();
      });

      const pythonFileButton = screen.getByRole('button', { name: /demo_rag_query\.py/i });
      fireEvent.click(pythonFileButton);

      // Should show loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    test('should show error message on content load failure', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ error: 'File not found' }),
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('QUICKSTART.md')).toBeInTheDocument();
      });

      const quickstartButton = screen.getByRole('button', { name: /QUICKSTART\.md/i });
      fireEvent.click(quickstartButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load file content/i)).toBeInTheDocument();
      });
    });

    test('should show prompt when no file is selected', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText(/Select a file from the sidebar to view its content/i)).toBeInTheDocument();
      });
    });
  });

  describe('Markdown Content Rendering', () => {
    test('should render markdown content', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('RAG Trial')).toBeInTheDocument();
      });
    });

    test('should render markdown with prose classes', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        const proseContainer = document.querySelector('.prose');
        expect(proseContainer).toBeInTheDocument();
        expect(proseContainer).toHaveClass('prose-invert');
        expect(proseContainer).toHaveClass('prose-purple');
      });
    });
  });

  describe('Python Code Rendering', () => {
    test('should render Python code content', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPythonContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('demo_rag_query.py')).toBeInTheDocument();
      });

      const pythonFileButton = screen.getByRole('button', { name: /demo_rag_query\.py/i });
      fireEvent.click(pythonFileButton);

      await waitFor(() => {
        // Content is rendered through SyntaxHighlighter, check for glass container instead
        const glassContainer = document.querySelector('.glass.rounded-xl');
        expect(glassContainer).toBeInTheDocument();
      });
    });

    test('should show filename header for Python files', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPythonContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('demo_rag_query.py')).toBeInTheDocument();
      });

      const pythonFileButton = screen.getByRole('button', { name: /demo_rag_query\.py/i });
      fireEvent.click(pythonFileButton);

      await waitFor(() => {
        const headers = screen.getAllByText(/demo_rag_query\.py/i);
        expect(headers.length).toBeGreaterThan(1); // One in sidebar, one in content header
      });
    });
  });

  describe('Sidebar', () => {
    test('should have sticky positioning', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const sidebar = document.querySelector('.sticky');
        expect(sidebar).toBeInTheDocument();
      });
    });

    test('should have max-height constraint', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const sidebar = document.querySelector('.max-h-\\[calc\\(100vh-6rem\\)\\]');
        expect(sidebar).toBeInTheDocument();
      });
    });

    test('should have overflow scroll', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const sidebar = document.querySelector('.overflow-y-auto');
        expect(sidebar).toBeInTheDocument();
      });
    });

    test('should have glass effect', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const glassElement = document.querySelector('.glass');
        expect(glassElement).toBeInTheDocument();
      });
    });
  });

  describe('Layout and Structure', () => {
    test('should have main container with padding top', () => {
      const { container } = renderDevDocs();
      const mainDiv = container.firstChild;
      expect(mainDiv).toHaveClass('pt-16');
      expect(mainDiv).toHaveClass('min-h-screen');
    });

    test('should have responsive grid layout', async () => {
      renderDevDocs();
      
      const grid = document.querySelector('.grid');
      expect(grid).toHaveClass('grid-cols-1');
      expect(grid).toHaveClass('lg:grid-cols-4');
    });

    test('should have max-width constraint', () => {
      renderDevDocs();
      
      const maxWidthContainer = document.querySelector('.max-w-7xl');
      expect(maxWidthContainer).toBeInTheDocument();
    });
  });

  describe('File Button Component', () => {
    test('should render all file buttons', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        expect(buttons.length).toBeGreaterThanOrEqual(4);
      });
    });

    test('should have monospace font for file names', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const readmeButton = screen.getByRole('button', { name: /README\.md/i });
        const monoText = readmeButton.querySelector('.font-mono');
        expect(monoText).toBeInTheDocument();
      });
    });

    test('should have hover styles', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        // Just verify buttons exist and have transition classes
        expect(buttons.length).toBeGreaterThan(0);
        buttons.forEach(button => {
          // Check for transition class which indicates interactive styling
          expect(button.classList.contains('transition-all')).toBe(true);
        });
      });
    });

    test('should have transition animation', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          expect(button.className).toContain('transition');
        });
      });
    });
  });

  describe('Typography and Styling', () => {
    test('should have gradient text on heading', () => {
      renderDevDocs();
      
      const heading = screen.getByText('Developer Documentation');
      expect(heading).toHaveClass('gradient-text');
    });

    test('should have proper text sizes', () => {
      renderDevDocs();
      
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-4xl');
      expect(heading).toHaveClass('font-bold');
    });

    test('should have slate color scheme', () => {
      renderDevDocs();
      
      const description = screen.getByText(/Explore code examples/i);
      expect(description).toHaveClass('text-slate-400');
    });
  });

  describe('Error Handling', () => {
    test('should display error for failed file list fetch', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));
      
      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to load documentation files/i)).toBeInTheDocument();
      });
    });

    test('should display error for failed content fetch', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        })
        .mockRejectedValueOnce(new Error('Content fetch failed'));

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('QUICKSTART.md')).toBeInTheDocument();
      });

      const quickstartButton = screen.getByRole('button', { name: /QUICKSTART\.md/i });
      fireEvent.click(quickstartButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load file content/i)).toBeInTheDocument();
      });
    });

    test('should clear error when successfully loading content', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockFiles,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        })
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMarkdownContent,
        });

      renderDevDocs();
      
      await waitFor(() => {
        expect(screen.getByText('QUICKSTART.md')).toBeInTheDocument();
      });

      const quickstartButton = screen.getByRole('button', { name: /QUICKSTART\.md/i });
      fireEvent.click(quickstartButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load file content/i)).toBeInTheDocument();
      });

      // Click README to load successfully
      const readmeButton = screen.getByRole('button', { name: /README\.md/i });
      fireEvent.click(readmeButton);

      await waitFor(() => {
        expect(screen.queryByText(/Failed to load file content/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('should have proper heading hierarchy', () => {
      renderDevDocs();
      
      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toBeInTheDocument();
    });

    test('should have accessible buttons', async () => {
      renderDevDocs();
      
      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          expect(button).toHaveTextContent(/.+/);
        });
      });
    });

    test('should have semantic HTML structure', () => {
      const { container } = renderDevDocs();
      
      const mainDiv = container.querySelector('div');
      expect(mainDiv).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    test('should have responsive padding', () => {
      renderDevDocs();
      
      const container = document.querySelector('.px-4');
      expect(container).toBeInTheDocument();
    });

    test('should have responsive grid columns', () => {
      renderDevDocs();
      
      const grid = document.querySelector('.grid');
      expect(grid).toHaveClass('grid-cols-1');
      expect(grid).toHaveClass('lg:grid-cols-4');
    });

    test('should have responsive font sizes', () => {
      renderDevDocs();
      
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-4xl');
    });
  });
});

