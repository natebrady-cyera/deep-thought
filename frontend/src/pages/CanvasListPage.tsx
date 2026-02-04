import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { canvasService, Canvas } from '../services/canvasService'

const CanvasListPage: React.FC = () => {
  const navigate = useNavigate()
  const [canvases, setCanvases] = useState<Canvas[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newCanvasName, setNewCanvasName] = useState('')
  const [newCanvasDescription, setNewCanvasDescription] = useState('')
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadCanvases()
  }, [])

  const loadCanvases = async () => {
    try {
      setLoading(true)
      const data = await canvasService.listCanvases()
      setCanvases(data)
    } catch (error) {
      console.error('Failed to load canvases:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCanvas = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newCanvasName.trim()) return

    try {
      setCreating(true)
      const canvas = await canvasService.createCanvas({
        name: newCanvasName,
        description: newCanvasDescription || undefined,
      })
      setShowCreateModal(false)
      setNewCanvasName('')
      setNewCanvasDescription('')
      // Navigate to the new canvas
      navigate(`/canvas/${canvas.id}`)
    } catch (error) {
      console.error('Failed to create canvas:', error)
      alert('Failed to create canvas')
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteCanvas = async (canvas: Canvas) => {
    if (!confirm(`Delete "${canvas.name}"?`)) return

    try {
      await canvasService.deleteCanvas(canvas.id)
      loadCanvases()
    } catch (error) {
      console.error('Failed to delete canvas:', error)
      alert('Failed to delete canvas')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  if (loading) {
    return (
      <div className="canvas-list-page">
        <div className="loading">Loading canvases...</div>
      </div>
    )
  }

  return (
    <div className="canvas-list-page">
      <div className="page-header">
        <h1>My Canvases</h1>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          + New Canvas
        </button>
      </div>

      {canvases.length === 0 ? (
        <div className="empty-state">
          <p>No canvases yet. Create your first deal canvas!</p>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            Create Canvas
          </button>
        </div>
      ) : (
        <div className="canvas-grid">
          {canvases.map((canvas) => (
            <div key={canvas.id} className="canvas-card">
              <div className="canvas-card-header">
                <h3 onClick={() => navigate(`/canvas/${canvas.id}`)}>{canvas.name}</h3>
                {canvas.is_shared && <span className="badge badge-shared">Shared</span>}
                {!canvas.can_write && <span className="badge badge-readonly">Read-only</span>}
              </div>

              <p className="canvas-description">{canvas.description || 'No description'}</p>

              <div className="canvas-meta">
                <span>Owner: {canvas.owner_email}</span>
                <span>{canvas.node_count} nodes</span>
              </div>

              <div className="canvas-footer">
                <span className="canvas-date">Updated {formatDate(canvas.updated_at)}</span>
                <div className="canvas-actions">
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => navigate(`/canvas/${canvas.id}`)}
                  >
                    Open
                  </button>
                  {canvas.is_owner && (
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteCanvas(canvas)}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Canvas</h2>
            <form onSubmit={handleCreateCanvas}>
              <div className="form-group">
                <label htmlFor="canvas-name">Name</label>
                <input
                  id="canvas-name"
                  type="text"
                  value={newCanvasName}
                  onChange={(e) => setNewCanvasName(e.target.value)}
                  placeholder="e.g., Acme Corp Enterprise Deal"
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label htmlFor="canvas-description">Description (optional)</label>
                <textarea
                  id="canvas-description"
                  value={newCanvasDescription}
                  onChange={(e) => setNewCanvasDescription(e.target.value)}
                  placeholder="Brief description of this deal..."
                  rows={3}
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                  disabled={creating}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Creating...' : 'Create Canvas'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default CanvasListPage
