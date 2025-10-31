import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import About from './About';

// Mock Footer component
vi.mock('../components/Footer', () => ({
  default: () => <div data-testid="footer-component">Footer Component</div>
}));

const renderAbout = () => {
  return render(
    <BrowserRouter>
      <About />
    </BrowserRouter>
  );
};

describe('About', () => {
  describe('Page Title Section', () => {
    test('should render page title', () => {
      renderAbout();
      expect(screen.getByText('About RAG Trial')).toBeInTheDocument();
    });

    test('should have gradient text on title', () => {
      renderAbout();
      const title = screen.getByText('About RAG Trial');
      expect(title).toHaveClass('gradient-text');
    });

    test('should have large font size for title', () => {
      renderAbout();
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-5xl');
      expect(heading).toHaveClass('font-bold');
    });

    test('should center align title', () => {
      renderAbout();
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-center');
    });
  });

  describe('What is RAG Trial Section', () => {
    test('should render section heading', () => {
      renderAbout();
      expect(screen.getByText('What is RAG Trial?')).toBeInTheDocument();
    });

    test('should render first paragraph', () => {
      renderAbout();
      expect(screen.getByText(/RAG Trial is a production-ready Retrieval-Augmented Generation/i)).toBeInTheDocument();
    });

    test('should render second paragraph', () => {
      renderAbout();
      expect(screen.getByText(/Built with modern technologies including FastAPI, LangChain, and React/i)).toBeInTheDocument();
    });

    test('should have glass effect styling', () => {
      renderAbout();
      const section = screen.getByText('What is RAG Trial?').closest('.glass');
      expect(section).toBeInTheDocument();
    });

    test('should have level 2 heading', () => {
      renderAbout();
      const heading = screen.getByRole('heading', { level: 2, name: 'What is RAG Trial?' });
      expect(heading).toBeInTheDocument();
    });
  });

  describe('Key Features Section', () => {
    test('should render section heading', () => {
      renderAbout();
      expect(screen.getByText('Key Features')).toBeInTheDocument();
    });

    test('should render Multi-Provider Support feature', () => {
      renderAbout();
      expect(screen.getByText(/Multi-Provider Support:/i)).toBeInTheDocument();
      expect(screen.getByText(/Integrate with OpenAI, Cohere, HuggingFace/i)).toBeInTheDocument();
    });

    test('should render Flexible Vector Stores feature', () => {
      renderAbout();
      expect(screen.getByText(/Flexible Vector Stores:/i)).toBeInTheDocument();
      expect(screen.getByText(/Support for Chroma, Pinecone, Qdrant, and Weaviate/i)).toBeInTheDocument();
    });

    test('should render Document Processing feature', () => {
      renderAbout();
      expect(screen.getByText(/Document Processing:/i)).toBeInTheDocument();
      expect(screen.getByText(/Upload and process various document formats/i)).toBeInTheDocument();
    });

    test('should render REST API feature', () => {
      renderAbout();
      expect(screen.getByText(/REST API:/i)).toBeInTheDocument();
      expect(screen.getByText(/Full-featured API for programmatic access/i)).toBeInTheDocument();
    });

    test('should render Interactive UI feature', () => {
      renderAbout();
      expect(screen.getByText(/Interactive UI:/i)).toBeInTheDocument();
      expect(screen.getByText(/Beautiful Streamlit-based chat interface/i)).toBeInTheDocument();
    });

    test('should render Production Ready feature', () => {
      renderAbout();
      expect(screen.getByText(/Production Ready:/i)).toBeInTheDocument();
      expect(screen.getByText(/Comprehensive logging, error handling, and monitoring/i)).toBeInTheDocument();
    });

    test('should have 6 feature list items', () => {
      renderAbout();
      const featuresSection = screen.getByText('Key Features').closest('.glass');
      if (featuresSection) {
        const listItems = featuresSection.querySelectorAll('li');
        expect(listItems).toHaveLength(6);
      }
    });

    test('should have bullet points for features', () => {
      renderAbout();
      const featuresSection = screen.getByText('Key Features').closest('.glass');
      if (featuresSection) {
        const bullets = featuresSection.querySelectorAll('.text-purple-400');
        expect(bullets.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Technology Stack Section', () => {
    test('should render section heading', () => {
      renderAbout();
      expect(screen.getByText('Technology Stack')).toBeInTheDocument();
    });

    test('should render Backend subsection', () => {
      renderAbout();
      expect(screen.getByText('Backend')).toBeInTheDocument();
    });

    test('should render Frontend subsection', () => {
      renderAbout();
      expect(screen.getByText('Frontend')).toBeInTheDocument();
    });

    test('should list Backend technologies', () => {
      renderAbout();
      const techSection = screen.getByText('Technology Stack').closest('.glass');
      if (techSection) {
        const backendSection = techSection.querySelector('h3.text-purple-400');
        expect(backendSection?.parentElement).toHaveTextContent('Python 3.12+');
        expect(backendSection?.parentElement).toHaveTextContent('FastAPI');
        expect(backendSection?.parentElement).toHaveTextContent('LangChain');
        expect(backendSection?.parentElement).toHaveTextContent('SQLAlchemy');
        expect(backendSection?.parentElement).toHaveTextContent('Pydantic');
      }
    });

    test('should list Frontend technologies', () => {
      renderAbout();
      expect(screen.getByText(/React 18/i)).toBeInTheDocument();
      expect(screen.getByText(/TypeScript/i)).toBeInTheDocument();
      expect(screen.getByText(/Tailwind CSS/i)).toBeInTheDocument();
      expect(screen.getByText(/Vite/i)).toBeInTheDocument();
      expect(screen.getByText(/Streamlit \(Chat UI\)/i)).toBeInTheDocument();
    });

    test('should have responsive grid for tech stacks', () => {
      renderAbout();
      const techSection = screen.getByText('Technology Stack').closest('.glass');
      if (techSection) {
        const grid = techSection.querySelector('.grid');
        expect(grid).toHaveClass('grid-cols-1');
        expect(grid).toHaveClass('md:grid-cols-2');
      }
    });

    test('should have colored headings for tech categories', () => {
      renderAbout();
      const backendHeading = screen.getByText('Backend').closest('h3');
      const frontendHeading = screen.getByText('Frontend').closest('h3');
      
      expect(backendHeading).toHaveClass('text-purple-400');
      expect(frontendHeading).toHaveClass('text-blue-400');
    });
  });

  describe('Getting Started Section', () => {
    test('should render section heading', () => {
      renderAbout();
      expect(screen.getByText('Getting Started')).toBeInTheDocument();
    });

    test('should render introduction text', () => {
      renderAbout();
      expect(screen.getByText(/To start using RAG Trial:/i)).toBeInTheDocument();
    });

    test('should have 5 steps', () => {
      renderAbout();
      const gettingStartedSection = screen.getByText('Getting Started').closest('.glass');
      if (gettingStartedSection) {
        const listItems = gettingStartedSection.querySelectorAll('li');
        expect(listItems).toHaveLength(5);
      }
    });

    test('should have ordered list for steps', () => {
      renderAbout();
      const gettingStartedSection = screen.getByText('Getting Started').closest('.glass');
      if (gettingStartedSection) {
        const orderedList = gettingStartedSection.querySelector('ol');
        expect(orderedList).toBeInTheDocument();
      }
    });

    test('should show step 1: Clone repository', () => {
      renderAbout();
      expect(screen.getByText(/Clone the repository from GitHub/i)).toBeInTheDocument();
    });

    test('should show step 2: Install dependencies', () => {
      renderAbout();
      expect(screen.getByText(/Install dependencies with/i)).toBeInTheDocument();
      expect(screen.getByText('make install')).toBeInTheDocument();
    });

    test('should show step 3: Configure API keys', () => {
      renderAbout();
      expect(screen.getByText(/Configure your LLM provider API keys/i)).toBeInTheDocument();
    });

    test('should show step 4: Run application', () => {
      renderAbout();
      expect(screen.getByText(/Run the application with/i)).toBeInTheDocument();
      expect(screen.getByText('make run')).toBeInTheDocument();
    });

    test('should show step 5: Access chat UI', () => {
      renderAbout();
      expect(screen.getByText(/Access the chat UI at/i)).toBeInTheDocument();
      expect(screen.getByText('/langchain/chat')).toBeInTheDocument();
    });

    test('should have code styling for commands', () => {
      renderAbout();
      const codeElements = document.querySelectorAll('code');
      expect(codeElements.length).toBeGreaterThan(0);
      codeElements.forEach(code => {
        expect(code).toHaveClass('bg-slate-950/50');
      });
    });
  });

  describe('GitHub Link Section', () => {
    test('should render View on GitHub button', () => {
      renderAbout();
      const githubLink = screen.getByRole('link', { name: /View on GitHub/i });
      expect(githubLink).toBeInTheDocument();
    });

    test('should have correct GitHub URL', () => {
      renderAbout();
      const githubLink = screen.getByRole('link', { name: /View on GitHub/i });
      expect(githubLink).toHaveAttribute('href', 'https://github.com/sanjibdevnathlabs/ragtrial');
    });

    test('should open in new tab', () => {
      renderAbout();
      const githubLink = screen.getByRole('link', { name: /View on GitHub/i });
      expect(githubLink).toHaveAttribute('target', '_blank');
    });

    test('should have proper rel attributes', () => {
      renderAbout();
      const githubLink = screen.getByRole('link', { name: /View on GitHub/i });
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
    });

    test('should have button styling', () => {
      renderAbout();
      const githubLink = screen.getByRole('link', { name: /View on GitHub/i });
      expect(githubLink).toHaveClass('btn-primary');
    });

    test('should be center aligned', () => {
      renderAbout();
      const container = screen.getByRole('link', { name: /View on GitHub/i }).closest('.text-center');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Footer Section', () => {
    test('should render Footer component', () => {
      renderAbout();
      expect(screen.getByTestId('footer-component')).toBeInTheDocument();
    });
  });

  describe('Layout and Structure', () => {
    test('should have main container with padding top', () => {
      const { container } = renderAbout();
      const mainDiv = container.firstChild;
      expect(mainDiv).toHaveClass('pt-16');
      expect(mainDiv).toHaveClass('min-h-screen');
    });

    test('should have max-width constraint', () => {
      renderAbout();
      const maxWidthContainer = document.querySelector('.max-w-4xl');
      expect(maxWidthContainer).toBeInTheDocument();
    });

    test('should have proper vertical spacing', () => {
      renderAbout();
      const contentContainer = document.querySelector('.space-y-8');
      expect(contentContainer).toBeInTheDocument();
    });

    test('should have all sections in glass containers', () => {
      renderAbout();
      const glassSections = document.querySelectorAll('.glass');
      expect(glassSections.length).toBe(4); // 4 main content sections
    });

    test('should have responsive padding', () => {
      renderAbout();
      const container = document.querySelector('.px-4');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Typography and Styling', () => {
    test('should have proper text colors', () => {
      renderAbout();
      const contentDiv = document.querySelector('.text-slate-300');
      expect(contentDiv).toBeInTheDocument();
    });

    test('should have large text size for content', () => {
      renderAbout();
      const contentDiv = document.querySelector('.text-lg');
      expect(contentDiv).toBeInTheDocument();
    });

    test('should have proper line height', () => {
      renderAbout();
      const contentDiv = document.querySelector('.leading-relaxed');
      expect(contentDiv).toBeInTheDocument();
    });

    test('should have white headings', () => {
      renderAbout();
      const h2Headings = screen.getAllByRole('heading', { level: 2 });
      h2Headings.forEach(heading => {
        expect(heading).toHaveClass('text-white');
      });
    });

    test('should have proper heading sizes', () => {
      renderAbout();
      const h2Headings = screen.getAllByRole('heading', { level: 2 });
      h2Headings.forEach(heading => {
        expect(heading).toHaveClass('text-2xl');
        expect(heading).toHaveClass('font-bold');
      });
    });
  });

  describe('Accessibility', () => {
    test('should have proper heading hierarchy', () => {
      renderAbout();
      
      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toBeInTheDocument();
      
      const h2Headings = screen.getAllByRole('heading', { level: 2 });
      expect(h2Headings.length).toBe(4);
      
      const h3Headings = screen.getAllByRole('heading', { level: 3 });
      expect(h3Headings.length).toBe(2);
    });

    test('should have descriptive link text', () => {
      renderAbout();
      const link = screen.getByRole('link', { name: /View on GitHub/i });
      expect(link.textContent).toBeTruthy();
    });

    test('should have semantic HTML structure', () => {
      const { container } = renderAbout();
      const mainDiv = container.querySelector('div');
      expect(mainDiv).toBeInTheDocument();
    });

    test('should have list structure for features', () => {
      renderAbout();
      const featuresSection = screen.getByText('Key Features').closest('.glass');
      if (featuresSection) {
        const list = featuresSection.querySelector('ul');
        expect(list).toBeInTheDocument();
      }
    });

    test('should have list structure for tech stack', () => {
      renderAbout();
      const techSection = screen.getByText('Technology Stack').closest('.glass');
      if (techSection) {
        const lists = techSection.querySelectorAll('ul');
        expect(lists.length).toBe(2); // Backend and Frontend
      }
    });

    test('should have ordered list for getting started steps', () => {
      renderAbout();
      const gettingStartedSection = screen.getByText('Getting Started').closest('.glass');
      if (gettingStartedSection) {
        const orderedList = gettingStartedSection.querySelector('ol');
        expect(orderedList).toBeInTheDocument();
      }
    });
  });

  describe('Responsive Design', () => {
    test('should have responsive padding', () => {
      renderAbout();
      const container = document.querySelector('.sm\\:px-6');
      expect(container).toBeInTheDocument();
    });

    test('should have responsive grid columns', () => {
      renderAbout();
      const grid = document.querySelector('.grid');
      expect(grid).toHaveClass('grid-cols-1');
      expect(grid).toHaveClass('md:grid-cols-2');
    });

    test('should have mobile-friendly layout', () => {
      renderAbout();
      const container = document.querySelector('.px-4');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Content Accuracy', () => {
    test('should mention all key technologies', () => {
      renderAbout();
      const techSection = screen.getByText('Technology Stack').closest('.glass');
      expect(techSection).toHaveTextContent('FastAPI');
      expect(techSection).toHaveTextContent('LangChain');
      expect(techSection).toHaveTextContent('React');
    });

    test('should mention vector store options', () => {
      renderAbout();
      expect(screen.getByText(/Chroma, Pinecone, Qdrant, and Weaviate/i)).toBeInTheDocument();
    });

    test('should mention LLM providers', () => {
      renderAbout();
      expect(screen.getByText(/OpenAI, Cohere, HuggingFace, Azure OpenAI/i)).toBeInTheDocument();
    });
  });
});

