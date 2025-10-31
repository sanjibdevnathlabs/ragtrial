import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import Navbar from './Navbar';

const renderNavbar = (initialRoute = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Navbar />
    </MemoryRouter>
  );
};

describe('Navbar', () => {
  describe('Logo and Branding', () => {
    it('should render the logo', () => {
      renderNavbar();
      expect(screen.getByText('R')).toBeInTheDocument();
      expect(screen.getByText('RAG Trial')).toBeInTheDocument();
    });

    it('should have logo link to home', () => {
      renderNavbar();
      const logoLink = screen.getByText('RAG Trial').closest('a');
      expect(logoLink).toHaveAttribute('href', '/');
    });
  });

  describe('Desktop Navigation Links', () => {
    it('should render all navigation links', () => {
      renderNavbar();
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Chat UI')).toBeInTheDocument();
      expect(screen.getByText('API Docs')).toBeInTheDocument();
      expect(screen.getByText('Dev Docs')).toBeInTheDocument();
      expect(screen.getByText('About')).toBeInTheDocument();
    });

    it('should highlight active link', () => {
      renderNavbar('/about');
      
      const homeLink = screen.getAllByText('Home')[0];
      const aboutLink = screen.getAllByText('About')[0];

      expect(homeLink.closest('a')).not.toHaveClass('bg-white/10');
      expect(aboutLink.closest('a')).toHaveClass('bg-white/10');
    });

    it('should render external links with correct href', () => {
      renderNavbar();
      
      // Chat UI is an external link
      const chatLinks = screen.getAllByText('Chat UI');
      const chatLink = chatLinks[0].closest('a');
      expect(chatLink).toHaveAttribute('href', '/langchain/chat');

      // API Docs is an external link
      const apiLinks = screen.getAllByText('API Docs');
      const apiLink = apiLinks[0].closest('a');
      expect(apiLink).toHaveAttribute('href', '/docs');
    });

    it('should render internal links with correct routing', () => {
      renderNavbar();
      
      const devDocsLinks = screen.getAllByText('Dev Docs');
      const devDocsLink = devDocsLinks[0].closest('a');
      expect(devDocsLink).toHaveAttribute('href', '/dev-docs');

      const aboutLinks = screen.getAllByText('About');
      const aboutLink = aboutLinks[0].closest('a');
      expect(aboutLink).toHaveAttribute('href', '/about');
    });

    it('should render GitHub link', () => {
      renderNavbar();
      
      const githubLink = screen.getByTitle('View on GitHub');
      expect(githubLink).toHaveAttribute('href', 'https://github.com/sanjibdevnathlabs/ragtrial');
      expect(githubLink).toHaveAttribute('target', '_blank');
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('should have GitHub icon SVG', () => {
      renderNavbar();
      
      const githubLink = screen.getByTitle('View on GitHub');
      const svg = githubLink.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Mobile Menu', () => {
    it('should not show mobile menu by default', () => {
      renderNavbar();
      
      // Mobile menu content should be hidden initially (only shows when isOpen is true)
      // The button exists, but the menu content (with border-t) should not be visible
      const allHomeLinks = screen.getAllByText('Home');
      // Should only have 1 "Home" link initially (desktop only, mobile menu hidden)
      expect(allHomeLinks.length).toBe(1);
    });

    it('should show mobile menu when hamburger button is clicked', () => {
      renderNavbar();
      
      const menuButton = screen.getByRole('button');
      fireEvent.click(menuButton);

      // All navigation links should appear twice (desktop + mobile)
      const homeLinks = screen.getAllByText('Home');
      expect(homeLinks.length).toBe(2); // Desktop + Mobile
    });

    it('should toggle mobile menu icon', () => {
      renderNavbar();
      
      const menuButton = screen.getByRole('button');
      const getPath = () => menuButton.querySelector('path')?.getAttribute('d');

      // Initially should show hamburger icon
      const initialPath = getPath();
      expect(initialPath).toContain('M4 6h16M4 12h16M4 18h16');

      // Click to open
      fireEvent.click(menuButton);
      const openPath = getPath();
      expect(openPath).toContain('M6 18L18 6M6 6l12 12');

      // Click to close
      fireEvent.click(menuButton);
      const closedPath = getPath();
      expect(closedPath).toContain('M4 6h16M4 12h16M4 18h16');
    });

    it('should close mobile menu when link is clicked', () => {
      renderNavbar();
      
      // Open mobile menu
      const menuButton = screen.getByRole('button');
      fireEvent.click(menuButton);

      // Mobile menu should be visible
      let homeLinks = screen.getAllByText('Home');
      expect(homeLinks.length).toBe(2);

      // Click a link in mobile menu (second occurrence is mobile)
      const mobileHomeLink = homeLinks[1];
      fireEvent.click(mobileHomeLink);

      // Mobile menu should close (only desktop link remains)
      homeLinks = screen.getAllByText('Home');
      expect(homeLinks.length).toBe(1);
    });

    it('should close mobile menu when external link is clicked', () => {
      renderNavbar();
      
      // Open mobile menu
      const menuButton = screen.getByRole('button');
      fireEvent.click(menuButton);

      // Click an external link in mobile menu
      const chatLinks = screen.getAllByText('Chat UI');
      const mobileChatLink = chatLinks[1]; // Second is mobile
      fireEvent.click(mobileChatLink);

      // Mobile menu should close
      const homeLinks = screen.getAllByText('Home');
      expect(homeLinks.length).toBe(1);
    });

    it('should highlight active link in mobile menu', () => {
      renderNavbar('/about');
      
      // Open mobile menu
      const menuButton = screen.getByRole('button');
      fireEvent.click(menuButton);

      const aboutLinks = screen.getAllByText('About');
      const mobileAboutLink = aboutLinks[1]; // Second is mobile

      expect(mobileAboutLink.closest('a')).toHaveClass('bg-white/10');
    });
  });

  describe('Responsive Behavior', () => {
    it('should have mobile menu button hidden on desktop', () => {
      renderNavbar();
      
      const menuButton = screen.getByRole('button');
      expect(menuButton).toHaveClass('md:hidden');
    });

    it('should have desktop navigation hidden on mobile', () => {
      renderNavbar();
      
      // Desktop nav has 'hidden md:flex' classes
      const desktopNav = document.querySelector('.hidden.md\\:flex');
      expect(desktopNav).toBeInTheDocument();
    });
  });

  describe('Styling and UI', () => {
    it('should have fixed positioning at top', () => {
      renderNavbar();
      
      const nav = document.querySelector('nav');
      expect(nav).toHaveClass('fixed', 'top-0', 'w-full', 'z-50');
    });

    it('should have glass effect styling', () => {
      renderNavbar();
      
      const nav = document.querySelector('nav');
      expect(nav).toHaveClass('glass');
    });

    it('should have gradient background on logo', () => {
      renderNavbar();
      
      const logoBox = screen.getByText('R').closest('div');
      expect(logoBox).toHaveClass('bg-gradient-to-br', 'from-purple-600', 'to-blue-600');
    });

    it('should apply hover styles to links', () => {
      renderNavbar();
      
      // Test on a non-active link (About) to check hover classes
      const aboutLink = screen.getAllByText('About')[0].closest('a');
      expect(aboutLink).toHaveClass('hover:text-white', 'hover:bg-white/10');
    });

    it('should apply transition effects', () => {
      renderNavbar();
      
      const homeLink = screen.getAllByText('Home')[0].closest('a');
      expect(homeLink).toHaveClass('transition-all', 'duration-200');
    });
  });

  describe('Accessibility', () => {
    it('should have accessible button for mobile menu', () => {
      renderNavbar();
      
      const menuButton = screen.getByRole('button');
      expect(menuButton).toBeInTheDocument();
    });

    it('should have proper link structure', () => {
      renderNavbar();
      
      const links = screen.getAllByRole('link');
      expect(links.length).toBeGreaterThan(0);

      // Each link should have either href or to attribute
      links.forEach(link => {
        const hasHref = link.hasAttribute('href');
        expect(hasHref).toBe(true);
      });
    });

    it('should have title attribute on GitHub link', () => {
      renderNavbar();
      
      const githubLink = screen.getByTitle('View on GitHub');
      expect(githubLink).toBeInTheDocument();
    });
  });

  describe('Active State Management', () => {
    it('should show home as active on root path', () => {
      renderNavbar('/');
      
      const homeLink = screen.getAllByText('Home')[0].closest('a');
      expect(homeLink).toHaveClass('bg-white/10');
    });

    it('should show dev docs as active on /dev-docs path', () => {
      renderNavbar('/dev-docs');
      
      const devDocsLink = screen.getAllByText('Dev Docs')[0].closest('a');
      expect(devDocsLink).toHaveClass('bg-white/10');
    });

    it('should show about as active on /about path', () => {
      renderNavbar('/about');
      
      const aboutLink = screen.getAllByText('About')[0].closest('a');
      expect(aboutLink).toHaveClass('bg-white/10');
    });

    it('should only have one active link at a time', () => {
      renderNavbar('/about');
      
      // Count links with active class
      const allLinks = screen.getAllByRole('link');
      const activeLinks = allLinks.filter(link => 
        link.className.includes('bg-white/10') && 
        link.className.includes('text-white') &&
        !link.className.includes('hover:bg-white/10') // Exclude links with only hover class
      );

      // Should have 1 active link (About)
      expect(activeLinks.length).toBe(1);
    });
  });

  describe('Navigation Structure', () => {
    it('should have correct number of navigation items', () => {
      renderNavbar();
      
      const navLinks = [
        'Home',
        'Chat UI',
        'API Docs',
        'Dev Docs',
        'About'
      ];

      navLinks.forEach(name => {
        // Each link appears once in desktop nav
        expect(screen.getByText(name)).toBeInTheDocument();
      });
    });

    it('should distinguish between internal and external links', () => {
      renderNavbar();
      
      // Internal links use <Link> (React Router)
      const devDocsLink = screen.getAllByText('Dev Docs')[0];
      expect(devDocsLink.closest('a')).toHaveAttribute('href', '/dev-docs');

      // External links use <a>
      const chatLink = screen.getAllByText('Chat UI')[0];
      expect(chatLink.closest('a')).toHaveAttribute('href', '/langchain/chat');
    });
  });
});

