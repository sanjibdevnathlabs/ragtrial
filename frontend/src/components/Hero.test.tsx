import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';
import Hero from './Hero';

describe('Hero', () => {
  describe('Content Rendering', () => {
    it('should render main heading', () => {
      render(<Hero />);
      
      expect(screen.getByText('RAG Application')).toBeInTheDocument();
      expect(screen.getByText('Made Simple')).toBeInTheDocument();
    });

    it('should render description text', () => {
      render(<Hero />);
      
      expect(screen.getByText(/Build powerful document search and retrieval systems/i)).toBeInTheDocument();
    });

    it('should have gradient text on main title', () => {
      render(<Hero />);
      
      const titleElement = screen.getByText('RAG Application');
      expect(titleElement).toHaveClass('gradient-text');
    });

    it('should render all content sections', () => {
      const { container } = render(<Hero />);
      
      // Main content container
      const contentContainer = container.querySelector('.relative.z-10');
      expect(contentContainer).toBeInTheDocument();
    });
  });

  describe('Call-to-Action Buttons', () => {
    it('should render "Try Chat UI" button', () => {
      render(<Hero />);
      
      expect(screen.getByText('Try Chat UI')).toBeInTheDocument();
    });

    it('should render "View API Docs" button', () => {
      render(<Hero />);
      
      expect(screen.getByText('View API Docs')).toBeInTheDocument();
    });

    it('should have correct href for Chat UI button', () => {
      render(<Hero />);
      
      const chatButton = screen.getByText('Try Chat UI').closest('a');
      expect(chatButton).toHaveAttribute('href', '/langchain/chat');
    });

    it('should have correct href for API Docs button', () => {
      render(<Hero />);
      
      const docsButton = screen.getByText('View API Docs').closest('a');
      expect(docsButton).toHaveAttribute('href', '/docs');
    });

    it('should have primary button styling on Chat UI button', () => {
      render(<Hero />);
      
      const chatButton = screen.getByText('Try Chat UI').closest('a');
      expect(chatButton).toHaveClass('btn-primary');
    });

    it('should have secondary button styling on API Docs button', () => {
      render(<Hero />);
      
      const docsButton = screen.getByText('View API Docs').closest('a');
      expect(docsButton).toHaveClass('btn-secondary');
    });

    it('should have glow animation on Chat UI button', () => {
      render(<Hero />);
      
      const chatButton = screen.getByText('Try Chat UI').closest('a');
      expect(chatButton).toHaveClass('animate-glow');
    });

    it('should render icons in buttons', () => {
      const { container } = render(<Hero />);
      
      const buttons = container.querySelectorAll('a svg');
      expect(buttons.length).toBeGreaterThanOrEqual(2); // At least 2 button icons
    });
  });

  describe('Stats Section', () => {
    it('should render all three stat cards', () => {
      const { container } = render(<Hero />);
      
      const statCards = container.querySelectorAll('.glass');
      // Should have 3 stat cards (stats section uses glass class)
      expect(statCards.length).toBeGreaterThanOrEqual(3);
    });

    it('should display LLM Providers stat', () => {
      render(<Hero />);
      
      expect(screen.getByText('5+')).toBeInTheDocument();
      expect(screen.getByText('LLM Providers')).toBeInTheDocument();
    });

    it('should display Vector Stores stat', () => {
      render(<Hero />);
      
      expect(screen.getByText('4+')).toBeInTheDocument();
      expect(screen.getByText('Vector Stores')).toBeInTheDocument();
    });

    it('should display Open Source stat', () => {
      render(<Hero />);
      
      expect(screen.getByText('100%')).toBeInTheDocument();
      expect(screen.getByText('Open Source')).toBeInTheDocument();
    });

    it('should have gradient text on stat numbers', () => {
      const { container } = render(<Hero />);
      
      const statNumbers = container.querySelectorAll('.text-3xl.font-bold.gradient-text');
      expect(statNumbers.length).toBe(3);
    });

    it('should have proper styling on stat labels', () => {
      const { container } = render(<Hero />);
      
      const llmLabel = screen.getByText('LLM Providers');
      expect(llmLabel).toHaveClass('text-slate-400');
    });

    it('should use grid layout for stats', () => {
      const { container } = render(<Hero />);
      
      const statsGrid = container.querySelector('.grid.grid-cols-1.md\\:grid-cols-3');
      expect(statsGrid).toBeInTheDocument();
    });
  });

  describe('Visual Elements', () => {
    it('should render animated gradient background', () => {
      const { container } = render(<Hero />);
      
      const gradientBg = container.querySelector('.animate-gradient');
      expect(gradientBg).toBeInTheDocument();
    });

    it('should render grid pattern overlay', () => {
      const { container } = render(<Hero />);
      
      const gridPattern = container.querySelector('[class*="bg-\\[linear-gradient"]');
      expect(gridPattern).toBeInTheDocument();
    });

    it('should render glowing orbs', () => {
      const { container } = render(<Hero />);
      
      const orbs = container.querySelectorAll('.rounded-full.filter.blur-3xl');
      expect(orbs.length).toBe(2);
    });

    it('should have different animation delays on orbs', () => {
      const { container } = render(<Hero />);
      
      const orbs = container.querySelectorAll('.rounded-full.filter.blur-3xl');
      const secondOrb = orbs[1] as HTMLElement;
      expect(secondOrb.style.animationDelay).toBe('2s');
    });

    it('should render scroll indicator', () => {
      const { container } = render(<Hero />);
      
      const scrollIndicator = container.querySelector('.animate-bounce');
      expect(scrollIndicator).toBeInTheDocument();
    });

    it('should have scroll indicator at bottom', () => {
      const { container } = render(<Hero />);
      
      // The animate-bounce div itself has absolute bottom-8 classes
      const scrollIndicator = container.querySelector('.animate-bounce');
      expect(scrollIndicator).toHaveClass('absolute', 'bottom-8');
    });
  });

  describe('Layout and Structure', () => {
    it('should have full screen height', () => {
      const { container } = render(<Hero />);
      
      const hero = container.firstChild as HTMLElement;
      expect(hero).toHaveClass('min-h-screen');
    });

    it('should center content', () => {
      const { container } = render(<Hero />);
      
      const hero = container.firstChild as HTMLElement;
      expect(hero).toHaveClass('flex', 'items-center', 'justify-center');
    });

    it('should have responsive padding', () => {
      const { container } = render(<Hero />);
      
      const contentWrapper = container.querySelector('.px-4.sm\\:px-6.lg\\:px-8');
      expect(contentWrapper).toBeInTheDocument();
    });

    it('should center text', () => {
      const { container } = render(<Hero />);
      
      const contentWrapper = container.querySelector('.text-center');
      expect(contentWrapper).toBeInTheDocument();
    });

    it('should have max width on content', () => {
      const { container } = render(<Hero />);
      
      const contentWrapper = container.querySelector('.max-w-5xl');
      expect(contentWrapper).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('should have responsive heading sizes', () => {
      render(<Hero />);
      
      const heading = screen.getByText('RAG Application').closest('h1');
      expect(heading).toHaveClass('text-5xl', 'md:text-7xl');
    });

    it('should have responsive description sizes', () => {
      render(<Hero />);
      
      const description = screen.getByText(/Build powerful document search/).closest('p');
      expect(description).toHaveClass('text-xl', 'md:text-2xl');
    });

    it('should have responsive button layout', () => {
      const { container } = render(<Hero />);
      
      const buttonContainer = container.querySelector('.flex.flex-col.sm\\:flex-row');
      expect(buttonContainer).toBeInTheDocument();
    });

    it('should have responsive stats grid', () => {
      const { container } = render(<Hero />);
      
      const statsGrid = container.querySelector('.grid-cols-1.md\\:grid-cols-3');
      expect(statsGrid).toBeInTheDocument();
    });
  });

  describe('Animations', () => {
    it('should animate main heading', () => {
      render(<Hero />);
      
      const heading = screen.getByText('RAG Application').closest('h1');
      expect(heading).toHaveClass('animate-float');
    });

    it('should have float animation on orbs', () => {
      const { container } = render(<Hero />);
      
      const orbs = container.querySelectorAll('.animate-float');
      expect(orbs.length).toBeGreaterThanOrEqual(2);
    });

    it('should have bounce animation on scroll indicator', () => {
      const { container } = render(<Hero />);
      
      const scrollIndicator = container.querySelector('.animate-bounce');
      expect(scrollIndicator).toBeInTheDocument();
    });

    it('should have gradient animation on background', () => {
      const { container } = render(<Hero />);
      
      const gradientBg = container.querySelector('.animate-gradient');
      expect(gradientBg).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have semantic heading element', () => {
      render(<Hero />);
      
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
    });

    it('should have descriptive button text', () => {
      render(<Hero />);
      
      const chatButton = screen.getByText('Try Chat UI');
      const docsButton = screen.getByText('View API Docs');

      expect(chatButton).toBeInTheDocument();
      expect(docsButton).toBeInTheDocument();
    });

    it('should use anchor tags for navigation', () => {
      const { container } = render(<Hero />);
      
      const links = container.querySelectorAll('a[href]');
      expect(links.length).toBeGreaterThanOrEqual(2);
    });

    it('should have proper heading hierarchy', () => {
      render(<Hero />);
      
      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1.textContent).toContain('RAG Application');
    });
  });

  describe('Typography', () => {
    it('should have bold heading', () => {
      render(<Hero />);
      
      const heading = screen.getByText('RAG Application').closest('h1');
      expect(heading).toHaveClass('font-bold');
    });

    it('should have proper line height on description', () => {
      render(<Hero />);
      
      const description = screen.getByText(/Build powerful document search/).closest('p');
      expect(description).toHaveClass('leading-relaxed');
    });

    it('should use white text for secondary heading', () => {
      render(<Hero />);
      
      const madeSimple = screen.getByText('Made Simple');
      expect(madeSimple).toHaveClass('text-white');
    });

    it('should use slate-300 for description', () => {
      render(<Hero />);
      
      const description = screen.getByText(/Build powerful document search/).closest('p');
      expect(description).toHaveClass('text-slate-300');
    });
  });

  describe('Content Accuracy', () => {
    it('should mention document search in description', () => {
      render(<Hero />);
      
      expect(screen.getByText(/document search and retrieval systems/i)).toBeInTheDocument();
    });

    it('should mention multi-provider LLM support', () => {
      render(<Hero />);
      
      expect(screen.getByText(/multi-provider LLM support/i)).toBeInTheDocument();
    });

    it('should mention vector embeddings', () => {
      render(<Hero />);
      
      expect(screen.getByText(/vector embeddings/i)).toBeInTheDocument();
    });

    it('should mention intelligent query processing', () => {
      render(<Hero />);
      
      expect(screen.getByText(/intelligent query processing/i)).toBeInTheDocument();
    });

    it('should show correct number of LLM providers', () => {
      render(<Hero />);
      
      expect(screen.getByText('5+')).toBeInTheDocument();
    });

    it('should show correct number of vector stores', () => {
      render(<Hero />);
      
      expect(screen.getByText('4+')).toBeInTheDocument();
    });

    it('should indicate 100% open source', () => {
      render(<Hero />);
      
      expect(screen.getByText('100%')).toBeInTheDocument();
    });
  });

  describe('Styling Classes', () => {
    it('should have glass effect on stat cards', () => {
      const { container } = render(<Hero />);
      
      const statCards = container.querySelectorAll('.glass.p-6.rounded-xl');
      expect(statCards.length).toBe(3);
    });

    it('should have relative positioning for layering', () => {
      const { container } = render(<Hero />);
      
      const hero = container.firstChild as HTMLElement;
      expect(hero).toHaveClass('relative');
    });

    it('should have overflow hidden', () => {
      const { container } = render(<Hero />);
      
      const hero = container.firstChild as HTMLElement;
      expect(hero).toHaveClass('overflow-hidden');
    });

    it('should have absolute positioned background elements', () => {
      const { container } = render(<Hero />);
      
      const absoluteElements = container.querySelectorAll('.absolute');
      expect(absoluteElements.length).toBeGreaterThan(3); // Background, grid, orbs, scroll indicator
    });
  });

  describe('Button Icons', () => {
    it('should render chat icon in Chat UI button', () => {
      const { container } = render(<Hero />);
      
      const chatButton = screen.getByText('Try Chat UI').closest('a');
      const icon = chatButton?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should render document icon in API Docs button', () => {
      const { container } = render(<Hero />);
      
      const docsButton = screen.getByText('View API Docs').closest('a');
      const icon = docsButton?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should have proper icon sizing', () => {
      const { container } = render(<Hero />);
      
      const buttonIcons = container.querySelectorAll('a svg.w-5.h-5');
      expect(buttonIcons.length).toBe(2);
    });

    it('should have icon margins', () => {
      const { container } = render(<Hero />);
      
      const buttonIcons = container.querySelectorAll('a svg.mr-2');
      expect(buttonIcons.length).toBe(2);
    });

    it('should render arrow icon in scroll indicator', () => {
      const { container } = render(<Hero />);
      
      const scrollIcon = container.querySelector('.animate-bounce svg');
      expect(scrollIcon).toBeInTheDocument();
      expect(scrollIcon).toHaveClass('w-6', 'h-6');
    });
  });

  describe('Z-Index Layering', () => {
    it('should have content above background', () => {
      const { container } = render(<Hero />);
      
      const content = container.querySelector('.relative.z-10');
      expect(content).toBeInTheDocument();
    });

    it('should have background elements behind content', () => {
      const { container } = render(<Hero />);
      
      const background = container.querySelector('.absolute.inset-0');
      expect(background).toBeInTheDocument();
    });
  });

  describe('Color Scheme', () => {
    it('should use purple-blue gradient theme', () => {
      const { container } = render(<Hero />);
      
      const gradientBg = container.querySelector('.from-purple-900\\/20');
      expect(gradientBg).toBeInTheDocument();
    });

    it('should have purple glowing orb', () => {
      const { container } = render(<Hero />);
      
      const purpleOrb = container.querySelector('.bg-purple-600\\/30');
      expect(purpleOrb).toBeInTheDocument();
    });

    it('should have blue glowing orb', () => {
      const { container } = render(<Hero />);
      
      const blueOrb = container.querySelector('.bg-blue-600\\/20');
      expect(blueOrb).toBeInTheDocument();
    });

    it('should use slate-400 for subtle text', () => {
      render(<Hero />);
      
      const statLabel = screen.getByText('LLM Providers');
      expect(statLabel).toHaveClass('text-slate-400');
    });
  });

  describe('Spacing and Margins', () => {
    it('should have proper spacing between heading and description', () => {
      render(<Hero />);
      
      const heading = screen.getByText('RAG Application').closest('h1');
      expect(heading).toHaveClass('mb-6');
    });

    it('should have proper spacing between description and buttons', () => {
      render(<Hero />);
      
      const description = screen.getByText(/Build powerful document search/).closest('p');
      expect(description).toHaveClass('mb-8');
    });

    it('should have proper spacing between buttons and stats', () => {
      const { container } = render(<Hero />);
      
      const buttonContainer = container.querySelector('.flex.flex-col.sm\\:flex-row');
      expect(buttonContainer).toHaveClass('mb-12');
    });

    it('should have gap between buttons', () => {
      const { container } = render(<Hero />);
      
      const buttonContainer = container.querySelector('.flex.flex-col.sm\\:flex-row');
      expect(buttonContainer).toHaveClass('gap-4');
    });
  });
});

