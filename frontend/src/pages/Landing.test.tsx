import { render, screen, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import Landing from './Landing';

// Mock child components
vi.mock('../components/Hero', () => ({
  default: () => <div data-testid="hero-component">Hero Component</div>
}));

vi.mock('../components/FeatureCard', () => ({
  default: ({ icon, title, description, delay }: any) => (
    <div data-testid="feature-card" data-delay={delay}>
      <span data-testid="feature-icon">{icon}</span>
      <h3 data-testid="feature-title">{title}</h3>
      <p data-testid="feature-description">{description}</p>
    </div>
  )
}));

vi.mock('../components/Footer', () => ({
  default: () => <div data-testid="footer-component">Footer Component</div>
}));

const renderLanding = () => {
  return render(
    <BrowserRouter>
      <Landing />
    </BrowserRouter>
  );
};

describe('Landing', () => {
  describe('Hero Section', () => {
    test('should render Hero component', () => {
      renderLanding();
      expect(screen.getByTestId('hero-component')).toBeInTheDocument();
    });
  });

  describe('Features Section', () => {
    test('should render features section heading', () => {
      renderLanding();
      expect(screen.getByText('Powerful Features')).toBeInTheDocument();
    });

    test('should render features section description', () => {
      renderLanding();
      expect(screen.getByText(/Everything you need to build production-ready RAG applications/i)).toBeInTheDocument();
    });

    test('should render 6 feature cards', () => {
      renderLanding();
      const featureCards = screen.getAllByTestId('feature-card');
      expect(featureCards).toHaveLength(6);
    });

    test('should render Multi-Provider Support feature', () => {
      renderLanding();
      expect(screen.getByText('Multi-Provider Support')).toBeInTheDocument();
      expect(screen.getByText(/Integrate with OpenAI, Cohere, HuggingFace/i)).toBeInTheDocument();
    });

    test('should render Document Processing feature', () => {
      renderLanding();
      expect(screen.getByText('Document Processing')).toBeInTheDocument();
      expect(screen.getByText(/Upload and process PDFs, text files, markdown/i)).toBeInTheDocument();
    });

    test('should render Intelligent Search feature', () => {
      renderLanding();
      expect(screen.getByText('Intelligent Search')).toBeInTheDocument();
      expect(screen.getByText(/Advanced RAG with source attribution/i)).toBeInTheDocument();
    });

    test('should render Vector Store Flexibility feature', () => {
      renderLanding();
      expect(screen.getByText('Vector Store Flexibility')).toBeInTheDocument();
      expect(screen.getByText(/Choose from Chroma, Pinecone, Qdrant, or Weaviate/i)).toBeInTheDocument();
    });

    test('should render Fast & Scalable feature', () => {
      renderLanding();
      expect(screen.getByText('Fast & Scalable')).toBeInTheDocument();
      expect(screen.getByText(/Built with FastAPI for high performance/i)).toBeInTheDocument();
    });

    test('should render Production Ready feature', () => {
      renderLanding();
      expect(screen.getByText('Production Ready')).toBeInTheDocument();
      expect(screen.getByText(/Comprehensive logging, error handling, health checks/i)).toBeInTheDocument();
    });

    test('should have correct feature icons', () => {
      renderLanding();
      const icons = screen.getAllByTestId('feature-icon');
      expect(icons[0]).toHaveTextContent('🚀');
      expect(icons[1]).toHaveTextContent('📁');
      expect(icons[2]).toHaveTextContent('🔍');
      expect(icons[3]).toHaveTextContent('🗄️');
      expect(icons[4]).toHaveTextContent('⚡');
      expect(icons[5]).toHaveTextContent('🔒');
    });

    test('should have staggered animation delays', () => {
      renderLanding();
      const cards = screen.getAllByTestId('feature-card');
      expect(cards[0]).toHaveAttribute('data-delay', '0s');
      expect(cards[1]).toHaveAttribute('data-delay', '0.2s');
      expect(cards[2]).toHaveAttribute('data-delay', '0.4s');
      expect(cards[3]).toHaveAttribute('data-delay', '0s');
      expect(cards[4]).toHaveAttribute('data-delay', '0.2s');
      expect(cards[5]).toHaveAttribute('data-delay', '0.4s');
    });
  });

  describe('Quick Start Section', () => {
    test('should render Quick Start heading', () => {
      renderLanding();
      expect(screen.getByText('Quick Start')).toBeInTheDocument();
    });

    test('should render Quick Start description', () => {
      renderLanding();
      expect(screen.getByText('Get up and running in minutes')).toBeInTheDocument();
    });

    test('should render API Usage heading', () => {
      renderLanding();
      expect(screen.getByText('API Usage')).toBeInTheDocument();
    });

    test('should render API Usage code example', () => {
      renderLanding();
      expect(screen.getByText(/curl -X POST http:\/\/localhost:8000\/api\/v1\/upload/)).toBeInTheDocument();
    });

    test('should render Python SDK heading', () => {
      renderLanding();
      expect(screen.getByText('Python SDK')).toBeInTheDocument();
    });

    test('should render Python SDK code example', () => {
      renderLanding();
      expect(screen.getByText(/from rag import RAGChain/)).toBeInTheDocument();
    });

    test('should have View Full Documentation link', () => {
      renderLanding();
      const docLink = screen.getByRole('link', { name: /View Full Documentation/i });
      expect(docLink).toBeInTheDocument();
      expect(docLink).toHaveAttribute('href', '/docs');
    });

    test('should have glass effect on Quick Start section', () => {
      renderLanding();
      const glassElements = document.querySelectorAll('.glass');
      expect(glassElements.length).toBeGreaterThan(0);
    });
  });

  describe('Use Cases Section', () => {
    test('should render Use Cases heading', () => {
      renderLanding();
      expect(screen.getByText('Use Cases')).toBeInTheDocument();
    });

    test('should render Use Cases description', () => {
      renderLanding();
      expect(screen.getByText(/Build intelligent applications for any industry/i)).toBeInTheDocument();
    });

    test('should render Knowledge Base use case', () => {
      renderLanding();
      expect(screen.getByText('Knowledge Base')).toBeInTheDocument();
      expect(screen.getByText('Internal documentation search')).toBeInTheDocument();
    });

    test('should render Customer Support use case', () => {
      renderLanding();
      expect(screen.getByText('Customer Support')).toBeInTheDocument();
      expect(screen.getByText('AI-powered help desk')).toBeInTheDocument();
    });

    test('should render Research Assistant use case', () => {
      renderLanding();
      expect(screen.getByText('Research Assistant')).toBeInTheDocument();
      expect(screen.getByText('Academic paper analysis')).toBeInTheDocument();
    });

    test('should render Legal Tech use case', () => {
      renderLanding();
      expect(screen.getByText('Legal Tech')).toBeInTheDocument();
      expect(screen.getByText('Contract and case search')).toBeInTheDocument();
    });

    test('should have 4 use case cards', () => {
      renderLanding();
      const useCaseSection = screen.getByText('Use Cases').closest('section');
      if (useCaseSection) {
        const cards = within(useCaseSection).getAllByRole('heading', { level: 4 });
        expect(cards).toHaveLength(4);
      }
    });

    test('should have hover transition classes on use case cards', () => {
      renderLanding();
      const useCaseSection = screen.getByText('Use Cases').closest('section');
      if (useCaseSection) {
        const cards = useCaseSection.querySelectorAll('.hover\\:scale-105');
        expect(cards.length).toBe(4);
      }
    });
  });

  describe('CTA Section', () => {
    test('should render CTA heading', () => {
      renderLanding();
      expect(screen.getByText('Ready to Get Started?')).toBeInTheDocument();
    });

    test('should render CTA description', () => {
      renderLanding();
      expect(screen.getByText(/Try our interactive chat interface or explore the API documentation/i)).toBeInTheDocument();
    });

    test('should have Launch Chat Interface button', () => {
      renderLanding();
      const chatButton = screen.getByRole('link', { name: /Launch Chat Interface/i });
      expect(chatButton).toBeInTheDocument();
      expect(chatButton).toHaveAttribute('href', '/langchain/chat');
    });

    test('should have Explore API button', () => {
      renderLanding();
      const apiButton = screen.getByRole('link', { name: /Explore API/i });
      expect(apiButton).toBeInTheDocument();
      expect(apiButton).toHaveAttribute('href', '/docs');
    });

    test('should have gradient background on CTA section', () => {
      renderLanding();
      const ctaSection = screen.getByText('Ready to Get Started?').closest('section');
      if (ctaSection) {
        const gradient = ctaSection.querySelector('.bg-gradient-to-r');
        expect(gradient).toBeInTheDocument();
      }
    });
  });

  describe('Footer Section', () => {
    test('should render Footer component', () => {
      renderLanding();
      expect(screen.getByTestId('footer-component')).toBeInTheDocument();
    });
  });

  describe('Layout and Structure', () => {
    test('should have main container with padding top', () => {
      const { container } = renderLanding();
      const mainDiv = container.firstChild;
      expect(mainDiv).toHaveClass('pt-16');
    });

    test('should have responsive grid for features', () => {
      renderLanding();
      const featuresSection = screen.getByText('Powerful Features').closest('section');
      if (featuresSection) {
        const grid = featuresSection.querySelector('.grid');
        expect(grid).toHaveClass('grid-cols-1');
        expect(grid).toHaveClass('md:grid-cols-3');
      }
    });

    test('should have responsive grid for Quick Start code examples', () => {
      renderLanding();
      const quickStartSection = screen.getByText('Quick Start').closest('section');
      if (quickStartSection) {
        const grid = quickStartSection.querySelector('.grid');
        expect(grid).toHaveClass('grid-cols-1');
        expect(grid).toHaveClass('md:grid-cols-2');
      }
    });

    test('should have responsive grid for use cases', () => {
      renderLanding();
      const useCasesSection = screen.getByText('Use Cases').closest('section');
      if (useCasesSection) {
        const grid = useCasesSection.querySelector('.grid');
        expect(grid).toHaveClass('grid-cols-1');
        expect(grid).toHaveClass('md:grid-cols-2');
        expect(grid).toHaveClass('lg:grid-cols-4');
      }
    });
  });

  describe('Typography and Styling', () => {
    test('should have gradient text on section headings', () => {
      renderLanding();
      const gradientTexts = document.querySelectorAll('.gradient-text');
      expect(gradientTexts.length).toBeGreaterThanOrEqual(4);
    });

    test('should have proper text sizes for headings', () => {
      renderLanding();
      const heading = screen.getByRole('heading', { name: /Powerful Features/i });
      expect(heading).toHaveClass('text-4xl');
      expect(heading).toHaveClass('md:text-5xl');
    });

    test('should have glass effect styling', () => {
      renderLanding();
      const glassElements = document.querySelectorAll('.glass');
      expect(glassElements.length).toBeGreaterThan(0);
    });
  });

  describe('Code Examples', () => {
    test('should show curl command for upload', () => {
      renderLanding();
      expect(screen.getByText(/curl -X POST.*\/api\/v1\/upload/)).toBeInTheDocument();
    });

    test('should show curl command for query', () => {
      renderLanding();
      expect(screen.getByText(/curl -X POST.*\/api\/v1\/query/)).toBeInTheDocument();
    });

    test('should show Python import statement', () => {
      renderLanding();
      expect(screen.getByText(/from rag import RAGChain/)).toBeInTheDocument();
    });

    test('should show Python query example', () => {
      renderLanding();
      expect(screen.getByText(/response = rag\.query/)).toBeInTheDocument();
    });

    test('should have monospace font for code', () => {
      renderLanding();
      const codeBlocks = document.querySelectorAll('.font-mono');
      expect(codeBlocks.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    test('should have proper heading hierarchy', () => {
      renderLanding();
      const h2Headings = screen.getAllByRole('heading', { level: 2 });
      expect(h2Headings.length).toBeGreaterThanOrEqual(4);
    });

    test('should have descriptive link text', () => {
      renderLanding();
      const links = screen.getAllByRole('link');
      links.forEach(link => {
        expect(link.textContent).toBeTruthy();
      });
    });

    test('should have semantic section elements', () => {
      const { container } = renderLanding();
      const sections = container.querySelectorAll('section');
      expect(sections.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('Responsive Design', () => {
    test('should have responsive padding classes', () => {
      renderLanding();
      const sections = document.querySelectorAll('section');
      sections.forEach(section => {
        const hasResponsivePadding = 
          section.className.includes('px-4') ||
          section.className.includes('sm:px-6') ||
          section.className.includes('lg:px-8');
        expect(hasResponsivePadding).toBe(true);
      });
    });

    test('should have max-width constraints', () => {
      renderLanding();
      const maxWidthElements = document.querySelectorAll('[class*="max-w-"]');
      expect(maxWidthElements.length).toBeGreaterThan(0);
    });

    test('should have responsive text sizes', () => {
      renderLanding();
      const responsiveText = document.querySelectorAll('[class*="md:text-"]');
      expect(responsiveText.length).toBeGreaterThan(0);
    });
  });
});

