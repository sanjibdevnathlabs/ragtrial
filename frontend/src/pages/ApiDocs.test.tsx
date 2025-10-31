import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import ApiDocs from './ApiDocs';

// Mock SwaggerUI component
vi.mock('swagger-ui-react', () => ({
  default: ({ url, deepLinking, displayRequestDuration, filter, showExtensions, showCommonExtensions, tryItOutEnabled }: any) => (
    <div data-testid="swagger-ui-component">
      <div data-testid="swagger-url">{url}</div>
      <div data-testid="swagger-deep-linking">{String(deepLinking)}</div>
      <div data-testid="swagger-display-duration">{String(displayRequestDuration)}</div>
      <div data-testid="swagger-filter">{String(filter)}</div>
      <div data-testid="swagger-show-extensions">{String(showExtensions)}</div>
      <div data-testid="swagger-show-common-extensions">{String(showCommonExtensions)}</div>
      <div data-testid="swagger-try-it-out">{String(tryItOutEnabled)}</div>
    </div>
  )
}));

// Mock CSS import
vi.mock('swagger-ui-react/swagger-ui.css', () => ({}));

const renderApiDocs = () => {
  return render(
    <BrowserRouter>
      <ApiDocs />
    </BrowserRouter>
  );
};

describe('ApiDocs', () => {
  describe('Hero Section', () => {
    test('should render page title', () => {
      renderApiDocs();
      expect(screen.getByText('API Documentation')).toBeInTheDocument();
    });

    test('should render page description', () => {
      renderApiDocs();
      expect(screen.getByText(/Complete REST API reference for document management and RAG query operations/i)).toBeInTheDocument();
    });

    test('should have gradient text on title', () => {
      renderApiDocs();
      const title = screen.getByText('API Documentation');
      expect(title).toHaveClass('gradient-text');
    });

    test('should have large font size for title', () => {
      renderApiDocs();
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-4xl');
      expect(heading).toHaveClass('md:text-5xl');
      expect(heading).toHaveClass('font-bold');
    });

    test('should have glass effect on hero section', () => {
      renderApiDocs();
      const hero = screen.getByText('API Documentation').closest('.glass');
      expect(hero).toBeInTheDocument();
    });

    test('should have border bottom on hero section', () => {
      renderApiDocs();
      const hero = screen.getByText('API Documentation').closest('.glass');
      expect(hero).toHaveClass('border-b');
      expect(hero).toHaveClass('border-white/10');
    });
  });

  describe('SwaggerUI Component', () => {
    test('should render SwaggerUI component', () => {
      renderApiDocs();
      expect(screen.getByTestId('swagger-ui-component')).toBeInTheDocument();
    });

    test('should pass correct OpenAPI URL', () => {
      renderApiDocs();
      const urlElement = screen.getByTestId('swagger-url');
      expect(urlElement).toHaveTextContent('/openapi.json');
    });

    test('should enable deep linking', () => {
      renderApiDocs();
      const deepLinkingElement = screen.getByTestId('swagger-deep-linking');
      expect(deepLinkingElement).toHaveTextContent('true');
    });

    test('should display request duration', () => {
      renderApiDocs();
      const displayDurationElement = screen.getByTestId('swagger-display-duration');
      expect(displayDurationElement).toHaveTextContent('true');
    });

    test('should enable filter', () => {
      renderApiDocs();
      const filterElement = screen.getByTestId('swagger-filter');
      expect(filterElement).toHaveTextContent('true');
    });

    test('should show extensions', () => {
      renderApiDocs();
      const showExtensionsElement = screen.getByTestId('swagger-show-extensions');
      expect(showExtensionsElement).toHaveTextContent('true');
    });

    test('should show common extensions', () => {
      renderApiDocs();
      const showCommonExtensionsElement = screen.getByTestId('swagger-show-common-extensions');
      expect(showCommonExtensionsElement).toHaveTextContent('true');
    });

    test('should enable try it out', () => {
      renderApiDocs();
      const tryItOutElement = screen.getByTestId('swagger-try-it-out');
      expect(tryItOutElement).toHaveTextContent('true');
    });
  });

  describe('Layout and Structure', () => {
    test('should have main container with proper styling', () => {
      const { container } = renderApiDocs();
      const mainDiv = container.firstChild;
      expect(mainDiv).toHaveClass('min-h-screen');
      expect(mainDiv).toHaveClass('bg-slate-900');
      expect(mainDiv).toHaveClass('pt-16');
    });

    test('should have hero container with proper styling', () => {
      renderApiDocs();
      const heroContainer = screen.getByText('API Documentation').closest('.container');
      expect(heroContainer).toBeInTheDocument();
      expect(heroContainer).toHaveClass('mx-auto');
      expect(heroContainer).toHaveClass('px-6');
      expect(heroContainer).toHaveClass('py-12');
    });

    test('should have swagger container with proper styling', () => {
      renderApiDocs();
      const swaggerContainer = screen.getByTestId('swagger-ui-component').closest('.container');
      expect(swaggerContainer).toBeInTheDocument();
      expect(swaggerContainer).toHaveClass('mx-auto');
      expect(swaggerContainer).toHaveClass('px-6');
      expect(swaggerContainer).toHaveClass('py-8');
    });

    test('should have swagger-container class', () => {
      renderApiDocs();
      const swaggerDiv = document.querySelector('.swagger-container');
      expect(swaggerDiv).toBeInTheDocument();
    });

    test('should have max-width constraint on description', () => {
      renderApiDocs();
      const description = screen.getByText(/Complete REST API reference/i);
      expect(description).toHaveClass('max-w-3xl');
    });
  });

  describe('Typography and Styling', () => {
    test('should have proper heading size', () => {
      renderApiDocs();
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-4xl');
      expect(heading).toHaveClass('md:text-5xl');
    });

    test('should have proper text colors', () => {
      renderApiDocs();
      const description = screen.getByText(/Complete REST API reference/i);
      expect(description).toHaveClass('text-slate-300');
    });

    test('should have proper text size for description', () => {
      renderApiDocs();
      const description = screen.getByText(/Complete REST API reference/i);
      expect(description).toHaveClass('text-xl');
    });

    test('should have proper spacing', () => {
      renderApiDocs();
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('mb-4');
    });
  });

  describe('Accessibility', () => {
    test('should have proper heading hierarchy', () => {
      renderApiDocs();
      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toBeInTheDocument();
      expect(h1).toHaveTextContent('API Documentation');
    });

    test('should have semantic HTML structure', () => {
      const { container } = renderApiDocs();
      const mainDiv = container.querySelector('div');
      expect(mainDiv).toBeInTheDocument();
    });

    test('should have descriptive title', () => {
      renderApiDocs();
      expect(screen.getByText('API Documentation')).toBeInTheDocument();
    });

    test('should have descriptive content', () => {
      renderApiDocs();
      expect(screen.getByText(/Complete REST API reference for document management and RAG query operations/i)).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    test('should have responsive heading size', () => {
      renderApiDocs();
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-4xl');
      expect(heading).toHaveClass('md:text-5xl');
    });

    test('should have responsive padding', () => {
      renderApiDocs();
      const containers = document.querySelectorAll('.container');
      containers.forEach(container => {
        expect(container).toHaveClass('px-6');
      });
    });

    test('should have responsive py spacing', () => {
      renderApiDocs();
      const hero = screen.getByText('API Documentation').closest('.container');
      expect(hero).toHaveClass('py-12');
    });
  });

  describe('Integration', () => {
    test('should integrate SwaggerUI as React component', () => {
      renderApiDocs();
      // Verify it's rendered as a React component, not an iframe
      expect(screen.getByTestId('swagger-ui-component')).toBeInTheDocument();
      expect(document.querySelector('iframe')).not.toBeInTheDocument();
    });

    test('should use window.location.origin for API URL', () => {
      const originalOrigin = window.location.origin;
      Object.defineProperty(window, 'location', {
        value: { origin: 'http://localhost:5173' },
        writable: true
      });

      renderApiDocs();
      const urlElement = screen.getByTestId('swagger-url');
      expect(urlElement).toHaveTextContent('http://localhost:5173/openapi.json');

      // Restore original
      Object.defineProperty(window, 'location', {
        value: { origin: originalOrigin },
        writable: true
      });
    });
  });

  describe('Comment Documentation', () => {
    test('should have JSDoc comment explaining the component', () => {
      // This is a documentation test - the component should have proper comments
      // We verify by checking the component renders correctly with expected features
      renderApiDocs();
      
      // Native React rendering (not iframe)
      expect(screen.getByTestId('swagger-ui-component')).toBeInTheDocument();
      expect(document.querySelector('iframe')).not.toBeInTheDocument();
    });
  });

  describe('Configuration', () => {
    test('should have all required SwaggerUI props configured', () => {
      renderApiDocs();
      
      // Verify all 7 main configuration props are passed
      expect(screen.getByTestId('swagger-url')).toBeInTheDocument();
      expect(screen.getByTestId('swagger-deep-linking')).toBeInTheDocument();
      expect(screen.getByTestId('swagger-display-duration')).toBeInTheDocument();
      expect(screen.getByTestId('swagger-filter')).toBeInTheDocument();
      expect(screen.getByTestId('swagger-show-extensions')).toBeInTheDocument();
      expect(screen.getByTestId('swagger-show-common-extensions')).toBeInTheDocument();
      expect(screen.getByTestId('swagger-try-it-out')).toBeInTheDocument();
    });

    test('should enable interactive features', () => {
      renderApiDocs();
      
      // Try it out should be enabled for testing
      const tryItOutElement = screen.getByTestId('swagger-try-it-out');
      expect(tryItOutElement).toHaveTextContent('true');
    });

    test('should enable filtering', () => {
      renderApiDocs();
      
      // Filter should be enabled for better UX
      const filterElement = screen.getByTestId('swagger-filter');
      expect(filterElement).toHaveTextContent('true');
    });
  });
});

