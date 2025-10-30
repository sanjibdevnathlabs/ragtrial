import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import Footer from '../components/Footer'

interface DocFile {
  name: string
  path: string
  type: string
  category: string
}

interface DocContent {
  name: string
  path: string
  type: string
  content: string
}

const DevDocs = () => {
  const [files, setFiles] = useState<DocFile[]>([])
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [content, setContent] = useState<DocContent | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch file list on mount
  useEffect(() => {
    fetch('/api/v1/devdocs/list')
      .then(res => res.json())
      .then(data => {
        setFiles(data)
        // Auto-select README.md if available
        const readme = data.find((f: DocFile) => f.name === 'README.md')
        if (readme) {
          setSelectedFile(readme.path)
        }
      })
      .catch(err => setError('Failed to load documentation files'))
  }, [])

  // Fetch content when file is selected
  useEffect(() => {
    if (!selectedFile) return

    setLoading(true)
    setError(null)

    fetch(`/api/v1/devdocs/content?file_path=${encodeURIComponent(selectedFile)}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to load content')
        return res.json()
      })
      .then(data => {
        setContent(data)
        setLoading(false)
      })
      .catch(err => {
        setError('Failed to load file content')
        setLoading(false)
      })
  }, [selectedFile])

  const categorizeFiles = () => {
    const categories: Record<string, DocFile[]> = {
      root: [],
      docs: [],
      examples: []
    }

    files.forEach(file => {
      categories[file.category].push(file)
    })

    return categories
  }

  const categories = categorizeFiles()

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
        </div>
      )
    }

    if (error) {
      return (
        <div className="glass p-8 rounded-xl">
          <p className="text-red-400">{error}</p>
        </div>
      )
    }

    if (!content) {
      return (
        <div className="glass p-8 rounded-xl">
          <p className="text-slate-400">Select a file from the sidebar to view its content</p>
        </div>
      )
    }

    if (content.type === 'markdown') {
      return (
        <div className="glass p-8 rounded-xl prose prose-invert prose-purple max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {content.content}
          </ReactMarkdown>
        </div>
      )
    }

    if (content.type === 'python') {
      return (
        <div className="glass rounded-xl overflow-hidden">
          <div className="bg-slate-800 px-4 py-2 border-b border-white/10">
            <p className="text-sm text-slate-400 font-mono">{content.name}</p>
          </div>
          <SyntaxHighlighter
            language="python"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              borderRadius: 0,
              background: 'transparent'
            }}
            showLineNumbers
          >
            {content.content}
          </SyntaxHighlighter>
        </div>
      )
    }

    return (
      <div className="glass p-8 rounded-xl">
        <pre className="whitespace-pre-wrap text-slate-300 font-mono text-sm">
          {content.content}
        </pre>
      </div>
    )
  }

  const FileButton = ({ file }: { file: DocFile }) => (
    <button
      onClick={() => setSelectedFile(file.path)}
      className={`w-full text-left px-3 py-2 rounded-lg transition-all duration-200 ${
        selectedFile === file.path
          ? 'bg-purple-600 text-white'
          : 'text-slate-300 hover:bg-white/10 hover:text-white'
      }`}
    >
      <span className="font-mono text-sm">{file.name}</span>
    </button>
  )

  return (
    <div className="pt-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            <span className="gradient-text">Developer Documentation</span>
          </h1>
          <p className="text-slate-400 text-lg">
            Explore code examples, guides, and API references
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="glass rounded-xl p-4 sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto">
              {/* README */}
              {categories.root.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-white font-semibold mb-2 px-3">Getting Started</h3>
                  <div className="space-y-1">
                    {categories.root.map(file => (
                      <FileButton key={file.path} file={file} />
                    ))}
                  </div>
                </div>
              )}

              {/* Documentation */}
              {categories.docs.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-white font-semibold mb-2 px-3">Documentation</h3>
                  <div className="space-y-1">
                    {categories.docs.map(file => (
                      <FileButton key={file.path} file={file} />
                    ))}
                  </div>
                </div>
              )}

              {/* Examples */}
              {categories.examples.length > 0 && (
                <div>
                  <h3 className="text-white font-semibold mb-2 px-3">Code Examples</h3>
                  <div className="space-y-1">
                    {categories.examples.map(file => (
                      <FileButton key={file.path} file={file} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {renderContent()}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}

export default DevDocs

