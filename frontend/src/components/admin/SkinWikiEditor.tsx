import { useState, useEffect } from 'react'
import {
  Plus,
  Edit2,
  Trash2,
  Save,
  X,
  History,
  Loader2,
  FileText,
} from 'lucide-react'
import { adminService } from '@/services/admin'
import type { WikiArticle, WikiVersion } from '@/types/admin'
import { useToast } from '@/hooks/useToast'

const CANCER_TYPES = [
  'Melanoma',
  'Basal Cell Carcinoma',
  'Squamous Cell Carcinoma',
  'Actinic Keratosis',
  'Dermatofibroma',
  'Nevus',
  'Vascular Lesion',
]

export default function SkinWikiEditor() {
  const [articles, setArticles] = useState<WikiArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [editingArticle, setEditingArticle] = useState<WikiArticle | null>(null)
  const [showVersions, setShowVersions] = useState<string | null>(null)
  const [versions, setVersions] = useState<WikiVersion[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    cancerType: '',
  })
  const { showToast } = useToast()

  useEffect(() => {
    loadArticles()
  }, [])

  const loadArticles = async () => {
    try {
      setLoading(true)
      const data = await adminService.getWikiArticles()
      setArticles(data)
    } catch (error) {
      showToast('Failed to load articles', 'error')
    } finally {
      setLoading(false)
    }
  }

  const loadVersions = async (articleId: string) => {
    try {
      const data = await adminService.getArticleVersions(articleId)
      setVersions(data)
      setShowVersions(articleId)
    } catch (error) {
      showToast('Failed to load version history', 'error')
    }
  }

  const handleCreate = () => {
    setIsCreating(true)
    setEditingArticle(null)
    setFormData({ title: '', content: '', cancerType: '' })
  }

  const handleEdit = (article: WikiArticle) => {
    setEditingArticle(article)
    setIsCreating(false)
    setFormData({
      title: article.title,
      content: article.content,
      cancerType: article.cancerType || '',
    })
  }

  const handleCancel = () => {
    setIsCreating(false)
    setEditingArticle(null)
    setFormData({ title: '', content: '', cancerType: '' })
  }

  const handleSave = async () => {
    try {
      if (!formData.title || !formData.content) {
        showToast('Title and content are required', 'error')
        return
      }

      if (editingArticle) {
        await adminService.updateWikiArticle(editingArticle.id, formData)
        showToast('Article updated successfully', 'success')
      } else {
        await adminService.createWikiArticle(formData)
        showToast('Article created successfully', 'success')
      }

      handleCancel()
      loadArticles()
    } catch (error) {
      showToast('Failed to save article', 'error')
    }
  }

  const handleDelete = async (articleId: string) => {
    if (!confirm('Are you sure you want to delete this article?')) return

    try {
      await adminService.deleteWikiArticle(articleId)
      showToast('Article deleted successfully', 'success')
      loadArticles()
    } catch (error) {
      showToast('Failed to delete article', 'error')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Skin-Wiki Editor</h2>
        <button onClick={handleCreate} className="btn btn-primary flex items-center gap-2">
          <Plus size={18} />
          New Article
        </button>
      </div>

      {/* Editor Form */}
      {(isCreating || editingArticle) && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            {editingArticle ? 'Edit Article' : 'Create New Article'}
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={e => setFormData({ ...formData, title: e.target.value })}
                className="input"
                placeholder="Article title"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cancer Type (Optional)
              </label>
              <select
                value={formData.cancerType}
                onChange={e =>
                  setFormData({ ...formData, cancerType: e.target.value })
                }
                className="input"
              >
                <option value="">Select cancer type</option>
                {CANCER_TYPES.map(type => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content
              </label>
              <textarea
                value={formData.content}
                onChange={e => setFormData({ ...formData, content: e.target.value })}
                className="input min-h-[300px] font-mono text-sm"
                placeholder="Article content (supports Markdown)"
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleSave}
                className="btn btn-primary flex items-center gap-2"
              >
                <Save size={18} />
                Save Article
              </button>
              <button
                onClick={handleCancel}
                className="btn btn-outline flex items-center gap-2"
              >
                <X size={18} />
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Articles List */}
      <div className="space-y-4">
        {articles.length === 0 ? (
          <div className="card text-center py-12">
            <FileText className="mx-auto text-gray-400 mb-2" size={48} />
            <p className="text-gray-600">No articles yet. Create your first article!</p>
          </div>
        ) : (
          articles.map(article => (
            <div key={article.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {article.title}
                  </h3>
                  {article.cancerType && (
                    <span className="inline-block mt-1 px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded">
                      {article.cancerType}
                    </span>
                  )}
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                    {article.content.substring(0, 150)}...
                  </p>
                  <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                    <span>Version {article.version}</span>
                    <span>Updated: {new Date(article.updatedAt).toLocaleDateString()}</span>
                    <span>By: {article.author}</span>
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => loadVersions(article.id)}
                    className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                    title="View version history"
                  >
                    <History size={18} />
                  </button>
                  <button
                    onClick={() => handleEdit(article)}
                    className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                    title="Edit article"
                  >
                    <Edit2 size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(article.id)}
                    className="p-2 text-danger-600 hover:bg-danger-50 rounded-lg"
                    title="Delete article"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Version History Modal */}
      {showVersions && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowVersions(null)}
        >
          <div
            className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Version History</h3>
                <button
                  onClick={() => setShowVersions(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X size={20} />
                </button>
              </div>

              <div className="space-y-4">
                {versions.map((version, index) => (
                  <div key={index} className="border-l-2 border-primary-600 pl-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">Version {version.version}</span>
                      <span className="text-sm text-gray-600">
                        {new Date(version.updatedAt).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">By: {version.author}</p>
                    <p className="text-sm text-gray-700 mt-2 line-clamp-3">
                      {version.content.substring(0, 200)}...
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
