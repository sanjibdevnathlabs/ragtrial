import Footer from '../components/Footer'

const About = () => {
  return (
    <div className="pt-16 min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h1 className="text-5xl font-bold mb-8 text-center">
          <span className="gradient-text">About RAG Trial</span>
        </h1>

        <div className="space-y-8 text-slate-300 text-lg leading-relaxed">
          <div className="glass p-8 rounded-2xl">
            <h2 className="text-2xl font-bold text-white mb-4">What is RAG Trial?</h2>
            <p className="mb-4">
              RAG Trial is a production-ready Retrieval-Augmented Generation (RAG) application 
              that combines the power of large language models with your own documents to provide 
              intelligent, context-aware responses.
            </p>
            <p>
              Built with modern technologies including FastAPI, LangChain, and React, it offers 
              a flexible and scalable solution for document search and question-answering systems.
            </p>
          </div>

          <div className="glass p-8 rounded-2xl">
            <h2 className="text-2xl font-bold text-white mb-4">Key Features</h2>
            <ul className="space-y-3">
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                <span><strong>Multi-Provider Support:</strong> Integrate with OpenAI, Cohere, HuggingFace, Azure OpenAI, and more</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                <span><strong>Flexible Vector Stores:</strong> Support for Chroma, Pinecone, Qdrant, and Weaviate</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                <span><strong>Document Processing:</strong> Upload and process various document formats</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                <span><strong>REST API:</strong> Full-featured API for programmatic access</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                <span><strong>Interactive UI:</strong> Beautiful Streamlit-based chat interface</span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                <span><strong>Production Ready:</strong> Comprehensive logging, error handling, and monitoring</span>
              </li>
            </ul>
          </div>

          <div className="glass p-8 rounded-2xl">
            <h2 className="text-2xl font-bold text-white mb-4">Technology Stack</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-lg font-semibold text-purple-400 mb-2">Backend</h3>
                <ul className="space-y-1 text-sm">
                  <li>• Python 3.12+</li>
                  <li>• FastAPI</li>
                  <li>• LangChain</li>
                  <li>• SQLAlchemy</li>
                  <li>• Pydantic</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-blue-400 mb-2">Frontend</h3>
                <ul className="space-y-1 text-sm">
                  <li>• React 18</li>
                  <li>• TypeScript</li>
                  <li>• Tailwind CSS</li>
                  <li>• Vite</li>
                  <li>• Streamlit (Chat UI)</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="glass p-8 rounded-2xl">
            <h2 className="text-2xl font-bold text-white mb-4">Getting Started</h2>
            <p className="mb-4">
              To start using RAG Trial:
            </p>
            <ol className="space-y-3 list-decimal list-inside">
              <li>Clone the repository from GitHub</li>
              <li>Install dependencies with <code className="bg-slate-950/50 px-2 py-1 rounded">make install</code></li>
              <li>Configure your LLM provider API keys</li>
              <li>Run the application with <code className="bg-slate-950/50 px-2 py-1 rounded">make run</code></li>
              <li>Access the chat UI at <code className="bg-slate-950/50 px-2 py-1 rounded">/langchain/chat</code></li>
            </ol>
          </div>

          <div className="text-center">
            <a
              href="https://github.com/sanjibdevnathlabs/ragtrial"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary inline-block"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}

export default About

