import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SourcesAccordion from './SourcesAccordion';

describe('SourcesAccordion', () => {
  const mockSources = [
    {
      filename: 'test1.pdf',
      chunk_index: 0,
      content: 'This is test content from document 1',
    },
    {
      filename: 'test2.pdf',
      chunk_index: 1,
      content: 'This is test content from document 2',
    },
  ];

  it('should render collapsed by default', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    expect(screen.getByText('Show Sources')).toBeInTheDocument();
    
    // Check that the content container has aria-hidden="true"
    const sourcesContent = document.getElementById('sources-content');
    expect(sourcesContent).toHaveAttribute('aria-hidden', 'true');
  });

  it('should show source count in collapsed state', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('should expand when clicked', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    const toggleButton = screen.getByRole('button');
    fireEvent.click(toggleButton);
    
    expect(screen.getByText('Hide Sources')).toBeInTheDocument();
    expect(screen.getByText(/test1\.pdf/)).toBeVisible();
    expect(screen.getByText(/test2\.pdf/)).toBeVisible();
  });

  it('should collapse when clicked again', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    const toggleButton = screen.getByRole('button');
    
    // Expand
    fireEvent.click(toggleButton);
    expect(screen.getByText('Hide Sources')).toBeInTheDocument();
    
    // Collapse
    fireEvent.click(toggleButton);
    expect(screen.getByText('Show Sources')).toBeInTheDocument();
  });

  it('should expand with Enter key', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    const toggleButton = screen.getByRole('button');
    fireEvent.keyDown(toggleButton, { key: 'Enter', code: 'Enter' });
    
    expect(screen.getByText('Hide Sources')).toBeInTheDocument();
  });

  it('should expand with Space key', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    const toggleButton = screen.getByRole('button');
    fireEvent.keyDown(toggleButton, { key: ' ', code: 'Space' });
    
    expect(screen.getByText('Hide Sources')).toBeInTheDocument();
  });

  it('should render expanded when defaultExpanded is true', () => {
    render(<SourcesAccordion sources={mockSources} defaultExpanded={true} />);
    
    expect(screen.getByText('Hide Sources')).toBeInTheDocument();
    expect(screen.getByText(/test1\.pdf/)).toBeVisible();
  });

  it('should display chunk indices', () => {
    render(<SourcesAccordion sources={mockSources} defaultExpanded={true} />);
    
    expect(screen.getByText('Chunk 0')).toBeInTheDocument();
    expect(screen.getByText('Chunk 1')).toBeInTheDocument();
  });

  it('should display source content', () => {
    render(<SourcesAccordion sources={mockSources} defaultExpanded={true} />);
    
    expect(screen.getByText('This is test content from document 1')).toBeInTheDocument();
    expect(screen.getByText('This is test content from document 2')).toBeInTheDocument();
  });

  it('should not render if sources array is empty', () => {
    const { container } = render(<SourcesAccordion sources={[]} />);
    
    expect(container.firstChild).toBeNull();
  });

  it('should not render if sources is undefined', () => {
    const { container } = render(<SourcesAccordion sources={undefined as any} />);
    
    expect(container.firstChild).toBeNull();
  });

  it('should have proper ARIA attributes', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
    expect(toggleButton).toHaveAttribute('aria-controls', 'sources-content');
    
    // Expand
    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
  });

  it('should show hint text when collapsed', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    expect(screen.getByText(/Click to see source references/i)).toBeInTheDocument();
  });

  it('should hide hint text when expanded', () => {
    render(<SourcesAccordion sources={mockSources} defaultExpanded={true} />);
    
    expect(screen.queryByText(/Click to see source references/i)).not.toBeInTheDocument();
  });

  it('should show info icon with tooltip', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toBeInTheDocument();
    
    // Info icon should be present (InformationCircleIcon)
    const svg = toggleButton.querySelector('svg[class*="w-4 h-4 text-slate-400"]');
    expect(svg).toBeInTheDocument();
  });

  it('should handle source without chunk_index', () => {
    const sourcesWithoutChunk = [
      {
        filename: 'test.pdf',
        chunk_index: undefined as any,
        content: 'Test content',
      },
    ];
    
    render(<SourcesAccordion sources={sourcesWithoutChunk} defaultExpanded={true} />);
    
    expect(screen.getByText(/test\.pdf/)).toBeInTheDocument();
    expect(screen.queryByText(/Chunk/)).not.toBeInTheDocument();
  });

  it('should apply hover styles', () => {
    render(<SourcesAccordion sources={mockSources} />);
    
    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toHaveClass('hover:bg-slate-800/30');
  });

  it('should show correct chevron icon when collapsed', () => {
    const { container } = render(<SourcesAccordion sources={mockSources} />);
    
    // ChevronDownIcon should be present when collapsed
    const chevronDown = container.querySelector('svg.text-purple-400');
    expect(chevronDown).toBeInTheDocument();
  });

  it('should show correct chevron icon when expanded', () => {
    const { container } = render(<SourcesAccordion sources={mockSources} defaultExpanded={true} />);
    
    // ChevronUpIcon should be present when expanded
    const chevronUp = container.querySelector('svg.text-purple-400');
    expect(chevronUp).toBeInTheDocument();
  });
});

