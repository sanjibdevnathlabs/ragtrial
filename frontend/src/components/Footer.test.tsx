import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import Footer from './Footer';

const renderFooter = () => {
  return render(
    <MemoryRouter>
      <Footer />
    </MemoryRouter>
  );
};

describe('Footer', () => {
  describe('Brand Section', () => {
    it('should render the logo', () => {
      renderFooter();
      
      expect(screen.getByText('R')).toBeInTheDocument();
      expect(screen.getByText('RAG Trial')).toBeInTheDocument();
    });

    it('should render brand description', () => {
      renderFooter();
      
      expect(screen.getByText(/Build intelligent document search systems/i)).toBeInTheDocument();
    });

    it('should have gradient logo background', () => {
      renderFooter();
      
      const logoBox = screen.getByText('R').closest('div');
      expect(logoBox).toHaveClass('bg-gradient-to-br', 'from-purple-600', 'to-blue-600');
    });

    it('should have gradient text on brand name', () => {
      renderFooter();
      
      const brandName = screen.getByText('RAG Trial');
      expect(brandName).toHaveClass('gradient-text');
    });

    it('should render GitHub link', () => {
      renderFooter();
      
      const githubLinks = screen.getAllByTitle('View on GitHub');
      expect(githubLinks.length).toBeGreaterThan(0);
      
      const githubLink = githubLinks[0];
      expect(githubLink).toHaveAttribute('href', 'https://github.com/sanjibdevnathlabs/ragtrial');
      expect(githubLink).toHaveAttribute('target', '_blank');
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('should have GitHub icon SVG', () => {
      renderFooter();
      
      const githubLink = screen.getAllByTitle('View on GitHub')[0];
      const svg = githubLink.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('w-6', 'h-6');
    });
  });

  describe('Quick Links Section', () => {
    it('should render Quick Links heading', () => {
      renderFooter();
      
      expect(screen.getByText('Quick Links')).toBeInTheDocument();
    });

    it('should render all quick links', () => {
      renderFooter();
      
      const quickLinksSection = screen.getByText('Quick Links').closest('div');
      expect(quickLinksSection).toBeInTheDocument();

      // Find all links - they appear in both Quick Links and potentially other sections
      expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'About' })).toBeInTheDocument();
      expect(screen.getAllByText('Chat UI').length).toBeGreaterThan(0);
      expect(screen.getAllByText('API Docs').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Dev Docs').length).toBeGreaterThan(0);
    });

    it('should have correct hrefs for quick links', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      
      const homeLink = links.find(link => link.textContent === 'Home');
      expect(homeLink).toHaveAttribute('href', '/');

      const aboutLink = links.find(link => link.textContent === 'About');
      expect(aboutLink).toHaveAttribute('href', '/about');

      const chatLink = links.find(link => link.textContent === 'Chat UI');
      expect(chatLink).toHaveAttribute('href', '/langchain/chat');

      const apiDocsLink = links.find(link => link.textContent === 'API Docs');
      expect(apiDocsLink).toHaveAttribute('href', '/docs');
    });

    it('should use Link component for internal routes', () => {
      renderFooter();
      
      // Internal routes use React Router Link
      const homeLink = screen.getByRole('link', { name: 'Home' });
      expect(homeLink).toHaveAttribute('href', '/');

      const aboutLink = screen.getByRole('link', { name: 'About' });
      expect(aboutLink).toHaveAttribute('href', '/about');
    });

    it('should use anchor tags for external routes', () => {
      renderFooter();
      
      // External routes use <a> tags
      const links = screen.getAllByRole('link');
      const chatLink = links.find(link => link.textContent === 'Chat UI');
      const apiDocsLink = links.find(link => link.textContent === 'API Docs');

      expect(chatLink?.tagName).toBe('A');
      expect(apiDocsLink?.tagName).toBe('A');
    });
  });

  describe('Resources Section', () => {
    it('should render Resources heading', () => {
      renderFooter();
      
      expect(screen.getByText('Resources')).toBeInTheDocument();
    });

    it('should render all resource links', () => {
      renderFooter();
      
      expect(screen.getByText('Documentation')).toBeInTheDocument();
      expect(screen.getByText('Examples')).toBeInTheDocument();
      expect(screen.getAllByText('GitHub')[0]).toBeInTheDocument();
      expect(screen.getByText('API Health')).toBeInTheDocument();
    });

    it('should have correct hrefs for resource links', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      
      const docsLink = links.find(link => link.textContent === 'Documentation');
      expect(docsLink).toHaveAttribute('href', '/dev-docs');

      const examplesLink = links.find(link => link.textContent === 'Examples');
      expect(examplesLink).toHaveAttribute('href', '/dev-docs');

      const githubLink = links.find(link => link.textContent === 'GitHub' && link.getAttribute('href')?.includes('github'));
      expect(githubLink).toHaveAttribute('href', 'https://github.com/sanjibdevnathlabs/ragtrial');

      const healthLink = links.find(link => link.textContent === 'API Health');
      expect(healthLink).toHaveAttribute('href', '/api/v1/health');
    });

    it('should open GitHub link in new tab', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      const githubLink = links.find(link => 
        link.textContent === 'GitHub' && 
        link.getAttribute('href')?.includes('github')
      );

      expect(githubLink).toHaveAttribute('target', '_blank');
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  describe('Copyright Section', () => {
    it('should render copyright notice', () => {
      renderFooter();
      
      const currentYear = new Date().getFullYear();
      expect(screen.getByText(new RegExp(`© ${currentYear} RAG Trial`))).toBeInTheDocument();
    });

    it('should display current year dynamically', () => {
      // Mock Date to test dynamic year
      const originalDate = global.Date;
      const mockDate = vi.fn(() => new originalDate('2025-01-15'));
      mockDate.prototype = originalDate.prototype;
      (global.Date as any) = mockDate;

      renderFooter();
      
      expect(screen.getByText(/© 2025 RAG Trial/)).toBeInTheDocument();

      // Restore original Date
      global.Date = originalDate;
    });

    it('should mention tech stack', () => {
      renderFooter();
      
      expect(screen.getByText(/Built with React, FastAPI, and LangChain/)).toBeInTheDocument();
    });

    it('should be centered', () => {
      renderFooter();
      
      const copyrightSection = screen.getByText(/Built with React/).closest('div');
      expect(copyrightSection).toHaveClass('text-center');
    });

    it('should have proper text color', () => {
      renderFooter();
      
      const copyrightSection = screen.getByText(/Built with React/).closest('div');
      expect(copyrightSection).toHaveClass('text-slate-400');
    });
  });

  describe('Layout and Structure', () => {
    it('should use semantic footer tag', () => {
      const { container } = renderFooter();
      
      const footer = container.querySelector('footer');
      expect(footer).toBeInTheDocument();
    });

    it('should have responsive grid layout', () => {
      const { container } = renderFooter();
      
      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('grid-cols-1', 'md:grid-cols-4');
    });

    it('should span brand section across 2 columns on desktop', () => {
      const { container } = renderFooter();
      
      const brandSection = screen.getByText('RAG Trial').closest('div')?.parentElement;
      expect(brandSection).toHaveClass('col-span-1', 'md:col-span-2');
    });

    it('should have proper spacing between sections', () => {
      const { container } = renderFooter();
      
      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('gap-8');
    });

    it('should have padding', () => {
      const { container } = renderFooter();
      
      const innerContainer = container.querySelector('.py-12');
      expect(innerContainer).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('should have border at top', () => {
      const { container } = renderFooter();
      
      const footer = container.querySelector('footer');
      expect(footer).toHaveClass('border-t', 'border-white/10');
    });

    it('should have background styling', () => {
      const { container } = renderFooter();
      
      const footer = container.querySelector('footer');
      expect(footer).toHaveClass('bg-slate-950/50', 'backdrop-blur-sm');
    });

    it('should have hover effects on links', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      const homeLink = links.find(link => link.textContent === 'Home');

      expect(homeLink).toHaveClass('hover:text-white', 'transition-colors');
    });

    it('should have proper text colors', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      const homeLink = links.find(link => link.textContent === 'Home');

      expect(homeLink).toHaveClass('text-slate-400');
    });

    it('should have section headings styled properly', () => {
      renderFooter();
      
      const quickLinksHeading = screen.getByText('Quick Links');
      expect(quickLinksHeading).toHaveClass('text-white', 'font-semibold', 'mb-4');

      const resourcesHeading = screen.getByText('Resources');
      expect(resourcesHeading).toHaveClass('text-white', 'font-semibold', 'mb-4');
    });

    it('should have proper list spacing', () => {
      const { container } = renderFooter();
      
      const lists = container.querySelectorAll('ul');
      lists.forEach(list => {
        expect(list).toHaveClass('space-y-2');
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      renderFooter();
      
      const headings = screen.getAllByRole('heading', { level: 3 });
      expect(headings.length).toBe(2); // Quick Links and Resources

      expect(headings[0].textContent).toBe('Quick Links');
      expect(headings[1].textContent).toBe('Resources');
    });

    it('should have descriptive link text', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      
      // All links should have meaningful text or a title attribute (for icon-only links)
      links.forEach(link => {
        const hasText = link.textContent?.trim() !== '';
        const hasTitle = link.getAttribute('title') !== null;
        expect(hasText || hasTitle).toBe(true);
      });
    });

    it('should have external links properly marked', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      const githubLinks = links.filter(link => 
        link.getAttribute('href')?.includes('github.com')
      );

      githubLinks.forEach(link => {
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
      });
    });

    it('should have title attribute on icon-only links', () => {
      renderFooter();
      
      const githubIconLink = screen.getAllByTitle('View on GitHub')[0];
      expect(githubIconLink).toBeInTheDocument();
    });
  });

  describe('Content Accuracy', () => {
    it('should have correct GitHub repository URL', () => {
      renderFooter();
      
      const links = screen.getAllByRole('link');
      const githubLinks = links.filter(link => 
        link.getAttribute('href') === 'https://github.com/sanjibdevnathlabs/ragtrial'
      );

      expect(githubLinks.length).toBeGreaterThan(0);
    });

    it('should have correct API health endpoint', () => {
      renderFooter();
      
      const healthLink = screen.getByText('API Health').closest('a');
      expect(healthLink).toHaveAttribute('href', '/api/v1/health');
    });

    it('should have multiple navigation items', () => {
      renderFooter();
      
      const allLinks = screen.getAllByRole('link');
      
      // Should have at least 10 links (Quick Links + Resources + Brand links)
      expect(allLinks.length).toBeGreaterThanOrEqual(10);
    });
  });

  describe('Responsive Design', () => {
    it('should have responsive container', () => {
      const { container } = renderFooter();
      
      const innerContainer = container.querySelector('.max-w-7xl');
      expect(innerContainer).toBeInTheDocument();
      expect(innerContainer).toHaveClass('mx-auto');
    });

    it('should have responsive padding', () => {
      const { container } = renderFooter();
      
      const innerContainer = container.querySelector('.max-w-7xl');
      expect(innerContainer).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
    });

    it('should stack sections on mobile', () => {
      const { container } = renderFooter();
      
      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('grid-cols-1');
    });

    it('should show 4 columns on desktop', () => {
      const { container } = renderFooter();
      
      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('md:grid-cols-4');
    });
  });

  describe('Visual Hierarchy', () => {
    it('should have brand section take more space', () => {
      const { container } = renderFooter();
      
      const brandSection = screen.getByText('RAG Trial').closest('div')?.parentElement;
      expect(brandSection).toHaveClass('md:col-span-2');
    });

    it('should separate copyright with border', () => {
      const { container } = renderFooter();
      
      const copyrightSection = screen.getByText(/Built with React/).closest('div');
      expect(copyrightSection).toHaveClass('border-t', 'border-white/10', 'mt-8', 'pt-8');
    });

    it('should have consistent spacing', () => {
      const { container } = renderFooter();
      
      const logo = screen.getByText('R').closest('div')?.parentElement;
      expect(logo).toHaveClass('mb-4');

      const description = screen.getByText(/Build intelligent/).closest('p');
      expect(description).toHaveClass('mb-4');
    });
  });

  describe('Copyright Year Update', () => {
    it('should update year automatically', () => {
      // Test with different years
      const testYears = [2024, 2025, 2026];

      testYears.forEach(year => {
        const originalDate = global.Date;
        const mockDate = vi.fn(() => new originalDate(`${year}-06-15`));
        mockDate.prototype = originalDate.prototype;
        (global.Date as any) = mockDate;

        const { unmount } = renderFooter();
        expect(screen.getByText(new RegExp(`© ${year}`))).toBeInTheDocument();
        
        unmount();
        global.Date = originalDate;
      });
    });
  });
});

