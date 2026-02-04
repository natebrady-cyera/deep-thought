import React, { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node as FlowNode,
  Edge,
  NodeChange,
  applyNodeChanges,
  Panel,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { canvasService } from '../services/canvasService'
import { nodeService, Node } from '../services/nodeService'
import GenericNode from '../components/nodes/GenericNode'
import ChatPanel from '../components/chat/ChatPanel'

const nodeTypes = {
  generic: GenericNode,
}

const CanvasPage: React.FC = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [canvas, setCanvas] = useState<any>(null)
  const [nodes, setNodes] = useState<FlowNode[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showAddNode, setShowAddNode] = useState(false)
  const [newNodeTitle, setNewNodeTitle] = useState('')
  const [showChat, setShowChat] = useState(false)

  // Load canvas and nodes
  useEffect(() => {
    if (!id) return
    loadCanvas()
  }, [id])

  const loadCanvas = async () => {
    try {
      setLoading(true)
      const [canvasData, nodesData] = await Promise.all([
        canvasService.getCanvas(Number(id)),
        nodeService.listCanvasNodes(Number(id)),
      ])

      setCanvas(canvasData)

      // Convert backend nodes to React Flow nodes
      const flowNodes: FlowNode[] = nodesData.map((node: Node) => ({
        id: String(node.id),
        type: node.node_type,
        position: { x: node.position_x, y: node.position_y },
        data: {
          ...node.data,
          label: node.title,
          nodeId: node.id,
          canvasId: node.canvas_id,
          onUpdate: (updates: any) => handleNodeDataUpdate(node.id, updates),
          onDelete: () => handleDeleteNode(node.id),
        },
        style: node.width && node.height ? { width: node.width, height: node.height } : undefined,
      }))

      setNodes(flowNodes)
    } catch (error) {
      console.error('Failed to load canvas:', error)
      alert('Failed to load canvas')
      navigate('/canvases')
    } finally {
      setLoading(false)
    }
  }

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      setNodes((nds) => applyNodeChanges(changes, nds))

      // Save position changes to backend
      const positionChanges = changes.filter(
        (change) => change.type === 'position' && change.dragging === false
      )

      if (positionChanges.length > 0) {
        handleSavePositions(positionChanges)
      }
    },
    []
  )

  const handleSavePositions = async (changes: any[]) => {
    try {
      setSaving(true)
      const updates = changes
        .filter((change) => change.position)
        .map((change) => ({
          id: Number(change.id),
          position_x: change.position.x,
          position_y: change.position.y,
        }))

      if (updates.length > 0) {
        await nodeService.bulkUpdatePositions(updates)
      }
    } catch (error) {
      console.error('Failed to save positions:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleNodeDataUpdate = async (nodeId: number, updates: any) => {
    try {
      await nodeService.updateNode(nodeId, updates)
      // Reload canvas to reflect changes
      loadCanvas()
    } catch (error) {
      console.error('Failed to update node:', error)
      alert('Failed to update node')
    }
  }

  const handleDeleteNode = async (nodeId: number) => {
    if (!confirm('Delete this node?')) return

    try {
      await nodeService.deleteNode(nodeId)
      setNodes((nds) => nds.filter((n) => n.id !== String(nodeId)))
    } catch (error) {
      console.error('Failed to delete node:', error)
      alert('Failed to delete node')
    }
  }

  const handleAddNode = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newNodeTitle.trim()) return

    try {
      // Calculate center position
      const centerX = window.innerWidth / 2 - 150
      const centerY = window.innerHeight / 2 - 100

      const newNode = await nodeService.createNode({
        canvas_id: Number(id),
        node_type: 'generic',
        title: newNodeTitle,
        position_x: centerX,
        position_y: centerY,
        data: { content: '' },
      })

      // Add to React Flow
      const flowNode: FlowNode = {
        id: String(newNode.id),
        type: 'generic',
        position: { x: newNode.position_x, y: newNode.position_y },
        data: {
          ...newNode.data,
          label: newNode.title,
          nodeId: newNode.id,
          canvasId: newNode.canvas_id,
          onUpdate: (updates: any) => handleNodeDataUpdate(newNode.id, updates),
          onDelete: () => handleDeleteNode(newNode.id),
        },
      }

      setNodes((nds) => [...nds, flowNode])
      setShowAddNode(false)
      setNewNodeTitle('')
    } catch (error) {
      console.error('Failed to create node:', error)
      alert('Failed to create node')
    }
  }

  if (loading) {
    return (
      <div className="canvas-page">
        <div className="loading">Loading canvas...</div>
      </div>
    )
  }

  if (!canvas) {
    return (
      <div className="canvas-page">
        <div className="error">Canvas not found</div>
      </div>
    )
  }

  return (
    <div className="canvas-page">
      <div className="canvas-header">
        <div>
          <button className="btn-back" onClick={() => navigate('/canvases')}>
            ← Back
          </button>
          <h1>{canvas.name}</h1>
        </div>
        <div className="canvas-actions">
          {saving && <span className="saving-indicator">Saving...</span>}
          <button className="btn btn-secondary" onClick={() => setShowChat(!showChat)}>
            🤖 AI Assistant
          </button>
          <button className="btn btn-primary" onClick={() => setShowAddNode(true)}>
            + Add Node
          </button>
        </div>
      </div>

      <div className={`canvas-container ${showChat ? 'chat-open' : ''}`}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          nodeTypes={nodeTypes}
          fitView
          defaultViewport={canvas.viewport || { x: 0, y: 0, zoom: 1 }}
        >
          <Background />
          <Controls />
          <MiniMap />
          <Panel position="bottom-right">
            <div style={{ background: 'white', padding: '0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem' }}>
              {nodes.length} node{nodes.length !== 1 ? 's' : ''}
            </div>
          </Panel>
        </ReactFlow>
      </div>

      {showAddNode && (
        <div className="modal-overlay" onClick={() => setShowAddNode(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add New Node</h2>
            <form onSubmit={handleAddNode}>
              <div className="form-group">
                <label htmlFor="node-title">Title</label>
                <input
                  id="node-title"
                  type="text"
                  value={newNodeTitle}
                  onChange={(e) => setNewNodeTitle(e.target.value)}
                  placeholder="e.g., Customer Requirements"
                  required
                  autoFocus
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowAddNode(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Add Node
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showChat && (
        <ChatPanel
          canvasId={Number(id)}
          onClose={() => setShowChat(false)}
        />
      )}
    </div>
  )
}

export default CanvasPage
