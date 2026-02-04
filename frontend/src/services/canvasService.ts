import api from './api'

export interface Canvas {
  id: number
  name: string
  description?: string
  owner_id: number
  owner_email: string
  is_archived: boolean
  created_at: string
  updated_at: string
  is_owner: boolean
  can_write: boolean
  is_shared: boolean
  node_count: number
}

export interface CreateCanvasData {
  name: string
  description?: string
}

export interface UpdateCanvasData {
  name?: string
  description?: string
  viewport?: {
    x: number
    y: number
    zoom: number
  }
}

export const canvasService = {
  // List all accessible canvases
  async listCanvases(includeArchived: boolean = false): Promise<Canvas[]> {
    const response = await api.get('/canvases/', {
      params: { include_archived: includeArchived }
    })
    return response.data
  },

  // Get canvas by ID
  async getCanvas(id: number) {
    const response = await api.get(`/canvases/${id}`)
    return response.data
  },

  // Create new canvas
  async createCanvas(data: CreateCanvasData) {
    const response = await api.post('/canvases/', data)
    return response.data
  },

  // Update canvas
  async updateCanvas(id: number, data: UpdateCanvasData) {
    const response = await api.put(`/canvases/${id}`, data)
    return response.data
  },

  // Delete canvas
  async deleteCanvas(id: number) {
    await api.delete(`/canvases/${id}`)
  },

  // Archive canvas
  async archiveCanvas(id: number) {
    const response = await api.post(`/canvases/${id}/archive`)
    return response.data
  },

  // Unarchive canvas
  async unarchiveCanvas(id: number) {
    const response = await api.post(`/canvases/${id}/unarchive`)
    return response.data
  },

  // Share canvas
  async shareCanvas(id: number, userEmail: string, canWrite: boolean = false) {
    const response = await api.post(`/canvases/${id}/share`, {
      user_email: userEmail,
      can_write: canWrite
    })
    return response.data
  },

  // Unshare canvas
  async unshareCanvas(id: number, userId: number) {
    await api.delete(`/canvases/${id}/share/${userId}`)
  },

  // List canvas shares
  async listShares(id: number) {
    const response = await api.get(`/canvases/${id}/shares`)
    return response.data
  },
}
