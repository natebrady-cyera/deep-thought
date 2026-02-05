import React, { useState, useRef, useEffect } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import './GenericNode.css'
import NodeChat from './NodeChat'

const getNodeTypeIcon = (nodeType: string): string => {
  const icons: { [key: string]: string } = {
    person: '👤',
    document: '📄',
    meeting: '📅',
    note: '📝',
    action: '✓',
    risk: '⚠️',
    competitor: '🏢',
    generic: '📦',
  }
  return icons[nodeType] || '📦'
}

const getNodeTypeLabel = (nodeType: string): string => {
  const labels: { [key: string]: string } = {
    person: 'Person',
    document: 'Document',
    meeting: 'Meeting',
    note: 'Note',
    action: 'Action',
    risk: 'Risk',
    competitor: 'Competitor',
    generic: 'Generic',
  }
  return labels[nodeType] || 'Generic'
}

const GenericNode: React.FC<NodeProps> = ({ data }) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [title, setTitle] = useState(data.label || '')
  const [activeTab, setActiveTab] = useState<'details' | 'chat'>('details')
  const [fields, setFields] = useState(data || {})
  const titleInputRef = useRef<HTMLInputElement>(null)
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (isEditingTitle && titleInputRef.current) {
      titleInputRef.current.focus()
      titleInputRef.current.select()
    }
  }, [isEditingTitle])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }
    }
  }, [])

  const handleTitleSave = () => {
    if (title !== data.label && title.trim()) {
      data.onUpdate({ title: title.trim() })
    }
    setIsEditingTitle(false)
  }

  const handleFieldUpdate = (fieldName: string, value: any) => {
    const updatedFields = { ...fields, [fieldName]: value }
    setFields(updatedFields)

    // Debounce the API call to avoid too many updates
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current)
    }

    updateTimeoutRef.current = setTimeout(() => {
      data.onUpdate({ data: updatedFields })
    }, 500) // Wait 500ms after user stops typing
  }

  const handleDelete = () => {
    if (data.onDelete) {
      data.onDelete()
    }
  }

  const renderFields = () => {
    const nodeType = data.nodeType || 'generic'

    switch (nodeType) {
      case 'person':
        return (
          <>
            <div className="field-group">
              <label>Name</label>
              <input
                type="text"
                value={fields.name || ''}
                onChange={(e) => handleFieldUpdate('name', e.target.value)}
                placeholder="Full name"
              />
            </div>
            <div className="field-group">
              <label>Role / Title</label>
              <input
                type="text"
                value={fields.role || ''}
                onChange={(e) => handleFieldUpdate('role', e.target.value)}
                placeholder="e.g., CISO, VP Engineering"
              />
            </div>
            <div className="field-group">
              <label>Email</label>
              <input
                type="email"
                value={fields.email || ''}
                onChange={(e) => handleFieldUpdate('email', e.target.value)}
                placeholder="email@company.com"
              />
            </div>
            <div className="field-group">
              <label>Phone</label>
              <input
                type="tel"
                value={fields.phone || ''}
                onChange={(e) => handleFieldUpdate('phone', e.target.value)}
                placeholder="Phone number"
              />
            </div>
            <div className="field-group">
              <label>Notes</label>
              <textarea
                value={fields.notes || ''}
                onChange={(e) => handleFieldUpdate('notes', e.target.value)}
                placeholder="Additional notes about this contact"
                rows={3}
              />
            </div>
          </>
        )

      case 'document':
        return (
          <>
            <div className="field-group">
              <label>Document Name</label>
              <input
                type="text"
                value={fields.documentName || ''}
                onChange={(e) => handleFieldUpdate('documentName', e.target.value)}
                placeholder="Name of the document"
              />
            </div>
            <div className="field-group">
              <label>Type</label>
              <select
                value={fields.documentType || 'other'}
                onChange={(e) => handleFieldUpdate('documentType', e.target.value)}
              >
                <option value="proposal">Proposal</option>
                <option value="contract">Contract</option>
                <option value="requirements">Requirements</option>
                <option value="presentation">Presentation</option>
                <option value="reference">Reference</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="field-group">
              <label>URL / Link</label>
              <input
                type="url"
                value={fields.url || ''}
                onChange={(e) => handleFieldUpdate('url', e.target.value)}
                placeholder="https://..."
              />
            </div>
            <div className="field-group">
              <label>Summary</label>
              <textarea
                value={fields.summary || ''}
                onChange={(e) => handleFieldUpdate('summary', e.target.value)}
                placeholder="Key points from this document"
                rows={4}
              />
            </div>
          </>
        )

      case 'meeting':
        return (
          <>
            <div className="field-group">
              <label>Date & Time</label>
              <input
                type="datetime-local"
                value={fields.date || ''}
                onChange={(e) => handleFieldUpdate('date', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>Attendees</label>
              <input
                type="text"
                value={fields.attendees || ''}
                onChange={(e) => handleFieldUpdate('attendees', e.target.value)}
                placeholder="Names or roles of attendees"
              />
            </div>
            <div className="field-group">
              <label>Agenda / Purpose</label>
              <textarea
                value={fields.agenda || ''}
                onChange={(e) => handleFieldUpdate('agenda', e.target.value)}
                placeholder="What was discussed"
                rows={2}
              />
            </div>
            <div className="field-group">
              <label>Notes / Outcomes</label>
              <textarea
                value={fields.notes || ''}
                onChange={(e) => handleFieldUpdate('notes', e.target.value)}
                placeholder="Key takeaways and action items"
                rows={4}
              />
            </div>
          </>
        )

      case 'action':
        return (
          <>
            <div className="field-group">
              <label>Assignee</label>
              <input
                type="text"
                value={fields.assignee || ''}
                onChange={(e) => handleFieldUpdate('assignee', e.target.value)}
                placeholder="Who is responsible"
              />
            </div>
            <div className="field-group">
              <label>Due Date</label>
              <input
                type="date"
                value={fields.dueDate || ''}
                onChange={(e) => handleFieldUpdate('dueDate', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>Status</label>
              <select
                value={fields.status || 'todo'}
                onChange={(e) => handleFieldUpdate('status', e.target.value)}
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="blocked">Blocked</option>
                <option value="done">Done</option>
              </select>
            </div>
            <div className="field-group">
              <label>Description</label>
              <textarea
                value={fields.description || ''}
                onChange={(e) => handleFieldUpdate('description', e.target.value)}
                placeholder="What needs to be done"
                rows={4}
              />
            </div>
          </>
        )

      case 'risk':
        return (
          <>
            <div className="field-group">
              <label>Severity</label>
              <select
                value={fields.severity || 'medium'}
                onChange={(e) => handleFieldUpdate('severity', e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div className="field-group">
              <label>Probability</label>
              <select
                value={fields.probability || 'medium'}
                onChange={(e) => handleFieldUpdate('probability', e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div className="field-group">
              <label>Description</label>
              <textarea
                value={fields.description || ''}
                onChange={(e) => handleFieldUpdate('description', e.target.value)}
                placeholder="What is the risk"
                rows={3}
              />
            </div>
            <div className="field-group">
              <label>Mitigation Plan</label>
              <textarea
                value={fields.mitigation || ''}
                onChange={(e) => handleFieldUpdate('mitigation', e.target.value)}
                placeholder="How to address this risk"
                rows={3}
              />
            </div>
          </>
        )

      case 'competitor':
        return (
          <>
            <div className="field-group">
              <label>Company Name</label>
              <input
                type="text"
                value={fields.companyName || ''}
                onChange={(e) => handleFieldUpdate('companyName', e.target.value)}
                placeholder="Competitor name"
              />
            </div>
            <div className="field-group">
              <label>Strengths</label>
              <textarea
                value={fields.strengths || ''}
                onChange={(e) => handleFieldUpdate('strengths', e.target.value)}
                placeholder="What they do well"
                rows={3}
              />
            </div>
            <div className="field-group">
              <label>Weaknesses</label>
              <textarea
                value={fields.weaknesses || ''}
                onChange={(e) => handleFieldUpdate('weaknesses', e.target.value)}
                placeholder="Where we can beat them"
                rows={3}
              />
            </div>
            <div className="field-group">
              <label>Notes</label>
              <textarea
                value={fields.notes || ''}
                onChange={(e) => handleFieldUpdate('notes', e.target.value)}
                placeholder="Additional competitive intelligence"
                rows={3}
              />
            </div>
          </>
        )

      case 'note':
      case 'generic':
      default:
        return (
          <div className="field-group">
            <label>Content</label>
            <textarea
              value={fields.content || ''}
              onChange={(e) => handleFieldUpdate('content', e.target.value)}
              placeholder="Enter your notes here..."
              rows={8}
            />
          </div>
        )
    }
  }

  return (
    <div className="generic-node">
      <Handle type="target" position={Position.Top} />

      <div className="node-header">
        <span className="node-type-icon" title={getNodeTypeLabel(data.nodeType || 'generic')}>
          {getNodeTypeIcon(data.nodeType || 'generic')}
        </span>
        {isEditingTitle ? (
          <input
            ref={titleInputRef}
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={handleTitleSave}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleTitleSave()
              } else if (e.key === 'Escape') {
                setTitle(data.label)
                setIsEditingTitle(false)
              }
            }}
            className="node-title-input"
          />
        ) : (
          <h4
            className="node-title"
            onDoubleClick={() => setIsEditingTitle(true)}
            title="Double-click to edit"
          >
            {data.label}
          </h4>
        )}

        <button className="node-delete" onClick={handleDelete} title="Delete node">
          ×
        </button>
      </div>

      <div className="node-tabs">
        <button
          className={`node-tab ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
        <button
          className={`node-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          Chat
        </button>
      </div>

      <div className="node-content">
        {activeTab === 'details' ? (
          <div className="node-fields">{renderFields()}</div>
        ) : (
          <NodeChat
            nodeId={data.nodeId}
            canvasId={data.canvasId}
            nodeTitle={data.label}
          />
        )}
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}

export default GenericNode
