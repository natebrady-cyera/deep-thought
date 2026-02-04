import React, { useState, useRef, useEffect } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import './GenericNode.css'

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
  const [isEditing, setIsEditing] = useState(false)
  const [content, setContent] = useState(data.content || '')
  const [title, setTitle] = useState(data.label || '')
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const titleInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [isEditing])

  useEffect(() => {
    if (isEditingTitle && titleInputRef.current) {
      titleInputRef.current.focus()
      titleInputRef.current.select()
    }
  }, [isEditingTitle])

  const handleContentSave = () => {
    if (content !== data.content) {
      data.onUpdate({ data: { ...data, content } })
    }
    setIsEditing(false)
  }

  const handleTitleSave = () => {
    if (title !== data.label && title.trim()) {
      data.onUpdate({ title: title.trim() })
    }
    setIsEditingTitle(false)
  }

  const handleDelete = () => {
    if (data.onDelete) {
      data.onDelete()
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

      <div className="node-content">
        {isEditing ? (
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onBlur={handleContentSave}
            placeholder="Enter your notes here..."
            rows={5}
          />
        ) : (
          <div
            className="node-content-display"
            onClick={() => setIsEditing(true)}
            title="Click to edit"
          >
            {content || <span className="placeholder">Click to add content...</span>}
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}

export default GenericNode
