import '@testing-library/jest-dom';

// Suppress jsdom navigation errors (known limitation)
// jsdom doesn't fully implement browser navigation APIs
const originalError = console.error;
const originalWarn = console.warn;

console.error = (...args: any[]) => {
  // Suppress specific jsdom navigation error
  if (
    typeof args[0] === 'string' &&
    args[0].includes('Not implemented: navigation')
  ) {
    return;
  }
  originalError.apply(console, args);
};

console.warn = (...args: any[]) => {
  // Suppress React Router v7 future flag warnings in tests
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('React Router Future Flag Warning') ||
     args[0].includes('v7_startTransition') ||
     args[0].includes('v7_relativeSplatPath'))
  ) {
    return;
  }
  originalWarn.apply(console, args);
};

