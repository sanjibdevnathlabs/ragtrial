import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';
import FeatureCard from './FeatureCard';

describe('FeatureCard', () => {
  const defaultProps = {
    icon: '🚀',
    title: 'Fast Performance',
    description: 'Lightning-fast document retrieval and query processing.',
  };

  describe('Rendering', () => {
    it('should render with all props', () => {
      render(<FeatureCard {...defaultProps} />);

      expect(screen.getByText('🚀')).toBeInTheDocument();
      expect(screen.getByText('Fast Performance')).toBeInTheDocument();
      expect(screen.getByText('Lightning-fast document retrieval and query processing.')).toBeInTheDocument();
    });

    it('should render icon correctly', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const iconElement = screen.getByText('🚀');
      expect(iconElement).toBeInTheDocument();
      expect(iconElement).toHaveClass('text-5xl', 'mb-4');
    });

    it('should render title correctly', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const titleElement = screen.getByText('Fast Performance');
      expect(titleElement).toBeInTheDocument();
      expect(titleElement.tagName).toBe('H3');
      expect(titleElement).toHaveClass('text-2xl', 'font-bold', 'mb-3', 'gradient-text');
    });

    it('should render description correctly', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const descriptionElement = screen.getByText('Lightning-fast document retrieval and query processing.');
      expect(descriptionElement).toBeInTheDocument();
      expect(descriptionElement.tagName).toBe('P');
      expect(descriptionElement).toHaveClass('text-slate-300', 'leading-relaxed');
    });
  });

  describe('Different Content', () => {
    it('should render different icons', () => {
      const icons = ['🔒', '⚡', '📚', '🎯'];
      
      icons.forEach(icon => {
        const { rerender } = render(<FeatureCard {...defaultProps} icon={icon} />);
        expect(screen.getByText(icon)).toBeInTheDocument();
        rerender(<div />); // Clean up between renders
      });
    });

    it('should render different titles', () => {
      const titles = ['Security First', 'High Performance', 'Rich Content', 'Precise Answers'];
      
      titles.forEach(title => {
        const { rerender } = render(<FeatureCard {...defaultProps} title={title} />);
        expect(screen.getByText(title)).toBeInTheDocument();
        rerender(<div />);
      });
    });

    it('should render different descriptions', () => {
      const descriptions = [
        'Enterprise-grade security for your documents.',
        'Process queries in milliseconds.',
        'Support for multiple document formats.',
      ];
      
      descriptions.forEach(description => {
        const { rerender } = render(<FeatureCard {...defaultProps} description={description} />);
        expect(screen.getByText(description)).toBeInTheDocument();
        rerender(<div />);
      });
    });

    it('should handle long titles', () => {
      const longTitle = 'This is a very long title that might wrap to multiple lines in the UI';
      render(<FeatureCard {...defaultProps} title={longTitle} />);
      
      expect(screen.getByText(longTitle)).toBeInTheDocument();
    });

    it('should handle long descriptions', () => {
      const longDescription = 'This is a very long description that provides detailed information about the feature and might span multiple lines when rendered in the actual user interface.';
      render(<FeatureCard {...defaultProps} description={longDescription} />);
      
      expect(screen.getByText(longDescription)).toBeInTheDocument();
    });

    it('should handle special characters in content', () => {
      render(
        <FeatureCard
          icon="🔐"
          title="Security & Privacy"
          description="Protect your data with 256-bit encryption & secure access."
        />
      );
      
      expect(screen.getByText('Security & Privacy')).toBeInTheDocument();
      expect(screen.getByText(/256-bit encryption & secure access/)).toBeInTheDocument();
    });
  });

  describe('Animation Delay', () => {
    it('should apply default delay of 0s when not specified', () => {
      const { container } = render(<FeatureCard {...defaultProps} />);
      
      const card = container.querySelector('.feature-card');
      expect(card).toHaveStyle({ animationDelay: '0s' });
    });

    it('should apply custom delay when specified', () => {
      const { container } = render(<FeatureCard {...defaultProps} delay="0.2s" />);
      
      const card = container.querySelector('.feature-card');
      expect(card).toHaveStyle({ animationDelay: '0.2s' });
    });

    it('should handle different delay values', () => {
      const delays = ['0.1s', '0.3s', '0.5s', '1s'];
      
      delays.forEach(delay => {
        const { container, rerender } = render(<FeatureCard {...defaultProps} delay={delay} />);
        const card = container.querySelector('.feature-card');
        expect(card).toHaveStyle({ animationDelay: delay });
        rerender(<div />);
      });
    });

    it('should handle millisecond delay values', () => {
      const { container } = render(<FeatureCard {...defaultProps} delay="200ms" />);
      
      const card = container.querySelector('.feature-card');
      expect(card).toHaveStyle({ animationDelay: '200ms' });
    });
  });

  describe('Styling and Classes', () => {
    it('should have feature-card class', () => {
      const { container } = render(<FeatureCard {...defaultProps} />);
      
      const card = container.querySelector('.feature-card');
      expect(card).toBeInTheDocument();
    });

    it('should have animate-float class', () => {
      const { container } = render(<FeatureCard {...defaultProps} />);
      
      const card = container.querySelector('.animate-float');
      expect(card).toBeInTheDocument();
    });

    it('should apply gradient-text to title', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const titleElement = screen.getByText('Fast Performance');
      expect(titleElement).toHaveClass('gradient-text');
    });

    it('should have proper icon size', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const iconElement = screen.getByText('🚀');
      expect(iconElement).toHaveClass('text-5xl');
    });

    it('should have proper spacing classes', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const iconElement = screen.getByText('🚀');
      const titleElement = screen.getByText('Fast Performance');

      expect(iconElement).toHaveClass('mb-4');
      expect(titleElement).toHaveClass('mb-3');
    });

    it('should have responsive text styles', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const titleElement = screen.getByText('Fast Performance');
      expect(titleElement).toHaveClass('text-2xl');
    });
  });

  describe('Structure', () => {
    it('should render elements in correct order', () => {
      const { container } = render(<FeatureCard {...defaultProps} />);
      
      const card = container.querySelector('.feature-card');
      const children = Array.from(card?.children || []);

      expect(children).toHaveLength(3);
      expect(children[0].textContent).toBe('🚀'); // Icon
      expect(children[1].textContent).toBe('Fast Performance'); // Title
      expect(children[2].textContent).toBe('Lightning-fast document retrieval and query processing.'); // Description
    });

    it('should wrap content in a single container div', () => {
      const { container } = render(<FeatureCard {...defaultProps} />);
      
      const cards = container.querySelectorAll('.feature-card');
      expect(cards).toHaveLength(1);
    });
  });

  describe('Accessibility', () => {
    it('should have heading element for title', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const heading = screen.getByRole('heading', { name: 'Fast Performance' });
      expect(heading).toBeInTheDocument();
      expect(heading.tagName).toBe('H3');
    });

    it('should have proper heading level', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const heading = screen.getByRole('heading', { level: 3 });
      expect(heading).toBeInTheDocument();
    });

    it('should have readable text content', () => {
      render(<FeatureCard {...defaultProps} />);
      
      const description = screen.getByText(/Lightning-fast document/);
      expect(description).toHaveClass('leading-relaxed'); // Good line height for readability
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty icon', () => {
      render(<FeatureCard {...defaultProps} icon="" />);
      
      // Icon element should still be rendered, just empty
      const card = document.querySelector('.feature-card');
      expect(card?.children[0]).toBeInTheDocument();
    });

    it('should handle empty title', () => {
      render(<FeatureCard {...defaultProps} title="" />);
      
      const headings = screen.queryAllByRole('heading');
      // H3 should exist but be empty
      expect(headings.length).toBeGreaterThan(0);
    });

    it('should handle empty description', () => {
      render(<FeatureCard {...defaultProps} description="" />);
      
      const paragraphs = document.querySelectorAll('p');
      expect(paragraphs.length).toBe(1);
    });

    it('should handle numeric strings as icon', () => {
      render(<FeatureCard {...defaultProps} icon="123" />);
      
      expect(screen.getByText('123')).toBeInTheDocument();
    });

    it('should handle HTML entities in text', () => {
      render(
        <FeatureCard
          {...defaultProps}
          title="Fast &amp; Secure"
          description="Protect &lt;your&gt; data"
        />
      );
      
      expect(screen.getByText('Fast & Secure')).toBeInTheDocument();
      expect(screen.getByText('Protect <your> data')).toBeInTheDocument();
    });
  });

  describe('Multiple Instances', () => {
    it('should render multiple cards independently', () => {
      const { container } = render(
        <>
          <FeatureCard icon="🚀" title="Fast" description="Speed" delay="0s" />
          <FeatureCard icon="🔒" title="Secure" description="Safety" delay="0.2s" />
          <FeatureCard icon="📚" title="Rich" description="Content" delay="0.4s" />
        </>
      );

      expect(screen.getByText('Fast')).toBeInTheDocument();
      expect(screen.getByText('Secure')).toBeInTheDocument();
      expect(screen.getByText('Rich')).toBeInTheDocument();

      const cards = container.querySelectorAll('.feature-card');
      expect(cards).toHaveLength(3);
    });

    it('should apply different delays to multiple cards', () => {
      const { container } = render(
        <>
          <FeatureCard {...defaultProps} delay="0s" />
          <FeatureCard {...defaultProps} delay="0.2s" />
          <FeatureCard {...defaultProps} delay="0.4s" />
        </>
      );

      const cards = container.querySelectorAll('.feature-card');
      expect(cards[0]).toHaveStyle({ animationDelay: '0s' });
      expect(cards[1]).toHaveStyle({ animationDelay: '0.2s' });
      expect(cards[2]).toHaveStyle({ animationDelay: '0.4s' });
    });
  });

  describe('Props Interface', () => {
    it('should accept all required props', () => {
      const props = {
        icon: '✨',
        title: 'Amazing Feature',
        description: 'This feature is truly amazing.',
      };

      expect(() => render(<FeatureCard {...props} />)).not.toThrow();
    });

    it('should accept optional delay prop', () => {
      const propsWithDelay = {
        ...defaultProps,
        delay: '1s',
      };

      expect(() => render(<FeatureCard {...propsWithDelay} />)).not.toThrow();
    });

    it('should work without delay prop', () => {
      expect(() => render(<FeatureCard {...defaultProps} />)).not.toThrow();
    });
  });
});

