import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';

/**
 * API Docs page component
 * 
 * Native React-rendered Swagger UI for better integration and performance.
 * No iframe needed - direct React component rendering.
 */
export default function ApiDocs() {
  return (
    <div className="min-h-screen bg-slate-900 pt-16">
      {/* Hero Section */}
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            <span className="gradient-text">API Documentation</span>
          </h1>
          <p className="text-slate-400 text-lg">
            Complete REST API reference for document management and RAG query operations
          </p>
        </div>
      </div>

      {/* Native Swagger UI - No iframe! */}
      <div className="container mx-auto px-6">
        <div className="swagger-container">
          <SwaggerUI
            url={`${window.location.origin}/openapi.json`}
            deepLinking={true}
            displayRequestDuration={true}
            filter={true}
            showExtensions={true}
            showCommonExtensions={true}
            tryItOutEnabled={true}
            docExpansion="list"
            defaultModelsExpandDepth={-1}
          />
        </div>
      </div>
    </div>
  );
}

