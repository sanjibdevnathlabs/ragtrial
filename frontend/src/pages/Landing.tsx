import Hero from '../components/Hero'
import FeatureCard from '../components/FeatureCard'
import Footer from '../components/Footer'

const Landing = () => {
  return (
    <div className="pt-16">
      {/* Hero Section */}
      <Hero />

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">Powerful Features</span>
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Everything you need to build production-ready RAG applications
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon="🚀"
              title="Multi-Provider Support"
              description="Integrate with OpenAI, Cohere, HuggingFace, Azure OpenAI, and more. Switch providers seamlessly without code changes."
              delay="0s"
            />
            <FeatureCard
              icon="📁"
              title="Document Processing"
              description="Upload and process PDFs, text files, markdown, and more. Automatic chunking and intelligent indexing for optimal retrieval."
              delay="0.2s"
            />
            <FeatureCard
              icon="🔍"
              title="Intelligent Search"
              description="Advanced RAG with source attribution, relevance scoring, and context-aware responses. Built on LangChain."
              delay="0.4s"
            />
            <FeatureCard
              icon="🗄️"
              title="Vector Store Flexibility"
              description="Choose from Chroma, Pinecone, Qdrant, or Weaviate. Local or cloud deployment options available."
              delay="0s"
            />
            <FeatureCard
              icon="⚡"
              title="Fast & Scalable"
              description="Built with FastAPI for high performance. Async operations, connection pooling, and optimized indexing."
              delay="0.2s"
            />
            <FeatureCard
              icon="🔒"
              title="Production Ready"
              description="Comprehensive logging, error handling, health checks, and monitoring. Docker support included."
              delay="0.4s"
            />
          </div>
        </div>
      </section>

      {/* Quick Start Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">Quick Start</span>
            </h2>
            <p className="text-xl text-slate-400">
              Get up and running in minutes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* API Usage */}
            <div className="glass p-8 rounded-2xl">
              <h3 className="text-2xl font-bold mb-4 text-white">API Usage</h3>
              <div className="bg-slate-950/50 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                <pre className="text-slate-300">
{`curl -X POST http://localhost:8000/api/v1/upload \\
  -F "file=@document.pdf"

curl -X POST http://localhost:8000/api/v1/query \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is RAG?",
    "top_k": 3
  }'`}
                </pre>
              </div>
            </div>

            {/* Python SDK */}
            <div className="glass p-8 rounded-2xl">
              <h3 className="text-2xl font-bold mb-4 text-white">Python SDK</h3>
              <div className="bg-slate-950/50 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                <pre className="text-slate-300">
{`from rag import RAGChain

# Initialize
rag = RAGChain()

# Upload document
rag.upload("document.pdf")

# Query
response = rag.query(
    "What is RAG?",
    top_k=3
)

print(response.answer)
print(response.sources)`}
                </pre>
              </div>
            </div>
          </div>

          <div className="mt-12 text-center">
            <a href="/docs" className="btn-primary inline-block">
              View Full Documentation
            </a>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">Use Cases</span>
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Build intelligent applications for any industry
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass p-6 rounded-xl text-center hover:scale-105 transition-all duration-300">
              <div className="text-4xl mb-3">📚</div>
              <h4 className="text-lg font-semibold mb-2 text-white">Knowledge Base</h4>
              <p className="text-slate-400 text-sm">Internal documentation search</p>
            </div>
            <div className="glass p-6 rounded-xl text-center hover:scale-105 transition-all duration-300">
              <div className="text-4xl mb-3">💼</div>
              <h4 className="text-lg font-semibold mb-2 text-white">Customer Support</h4>
              <p className="text-slate-400 text-sm">AI-powered help desk</p>
            </div>
            <div className="glass p-6 rounded-xl text-center hover:scale-105 transition-all duration-300">
              <div className="text-4xl mb-3">📊</div>
              <h4 className="text-lg font-semibold mb-2 text-white">Research Assistant</h4>
              <p className="text-slate-400 text-sm">Academic paper analysis</p>
            </div>
            <div className="glass p-6 rounded-xl text-center hover:scale-105 transition-all duration-300">
              <div className="text-4xl mb-3">⚖️</div>
              <h4 className="text-lg font-semibold mb-2 text-white">Legal Tech</h4>
              <p className="text-slate-400 text-sm">Contract and case search</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/20 to-blue-900/20"></div>
        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="gradient-text">Ready to Get Started?</span>
          </h2>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            Try our interactive chat interface or explore the API documentation
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/langchain/chat" className="btn-primary">
              Launch Chat Interface
            </a>
            <a href="/docs" className="btn-secondary">
              Explore API
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  )
}

export default Landing

