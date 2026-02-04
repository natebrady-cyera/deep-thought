import api from './api'

export interface Node {
  id: number
  canvas_id: number
  node_type: string
  title: string
  position_x: number
  position_y: number
  width?: number
  height?: number
  data: Record<string, any>
  exclude_from_context: boolean
  content_size?: number
  status?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface CreateNodeData {
  canvas_id: number
  node_type: string
  title: string
  position_x: number
  position_y: number
  data?: Record<string, any>
  width?: number
  height?: number
}

export interface UpdateNodeData {
  title?: string
  position_x?: number
  position_y?: number
  width?: number
  height?: number
  data?: Record<string, any>
  exclude_from_context?: boolean
  status?: Record<string, any>
}

export const nodeService = {
  // List available node types
  async getNodeTypes() {
    const response = await api.get('/nodes/types')
    return response.data.node_types
  },

  // List all nodes for a canvas
  async listCanvasNodes(canvasId: number): Promise<Node[]> {
    const response = await api.get(`/nodes/canvas/${canvasId}`)
    return response.data
  },

  // Get node by ID
  async getNode(id: number): Promise<Node> {
    const response = await api.get(`/nodes/${id}`)
    return response.data
  },

  // Create new node
  async createNode(data: CreateNodeData): Promise<Node> {
    const response = await api.post('/nodes/', data)
    return response.data
  },

  // Update node
  async updateNode(id: number, data: UpdateNodeData): Promise<Node> {
    const response = await api.put(`/nodes/${id}`, data)
    return response.data
  },

  // Delete node
  async deleteNode(id: number) {
    await api.delete(`/nodes/${id}`)
  },

  // Bulk update node positions
  async bulkUpdatePositions(updates: Array<{ id: number; position_x: number; position_y: number }>) {
    const response = await api.post('/nodes/bulk-update-positions', { updates })
    return response.data
  },
}
