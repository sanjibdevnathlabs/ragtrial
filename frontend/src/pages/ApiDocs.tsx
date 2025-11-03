import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import './ApiDocs.css';

/**
 * API Docs page component
 * 
 * Native React-rendered Swagger UI for better integration and performance.
 * No iframe needed - direct React component rendering.
 */
export default function ApiDocs() {
  return (
    <div className="min-h-screen bg-slate-900 pt-16">
      {/* Native Swagger UI - Maximized space for API content */}
      <div className="container mx-auto px-6 pt-4 pb-12">
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
  );
}

