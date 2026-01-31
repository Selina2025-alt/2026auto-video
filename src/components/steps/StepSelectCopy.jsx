import React, { useState } from 'react'
import './Steps.css'

function StepSelectCopy({ copywritingList, onComplete, onBack }) {
  const [selectedItems, setSelectedItems] = useState([])
  const [showAll, setShowAll] = useState(false)
  const [expandedItems, setExpandedItems] = useState({})

  const handleSelectAll = () => {
    if (selectedItems.length === copywritingList.length) {
      setSelectedItems([])
    } else {
      setSelectedItems(copywritingList.map(item => item.record_id))
    }
  }

  const handleSelectItem = (recordId) => {
    if (selectedItems.includes(recordId)) {
      setSelectedItems(selectedItems.filter(id => id !== recordId))
    } else {
      setSelectedItems([...selectedItems, recordId])
    }
  }

  const toggleExpand = (recordId, e) => {
    e.stopPropagation()
    setExpandedItems(prev => ({
      ...prev,
      [recordId]: !prev[recordId]
    }))
  }

  const toggleShowAll = () => {
    setShowAll(!showAll)
  }

  // 默认显示2条，其他折叠
  const displayedList = showAll ? copywritingList : copywritingList.slice(0, 2)
  const hiddenCount = copywritingList.length - 2

  const handleSubmit = (e) => {
    e.preventDefault()
    const selected = copywritingList.filter(item => 
      selectedItems.includes(item.record_id)
    )
    onComplete(selected)
  }

  return (
    <div className="step-container">
      <div className="step-header">
        <h2>📝 步骤 2: 选择要处理的文案</h2>
        <p>从飞书表格中选择需要生成视频的文案（可多选）</p>
        <p style={{ fontSize: '0.9rem', color: '#667eea', marginTop: '0.5rem' }}>
          🧪 测试模式：已加载模拟文案数据
        </p>
      </div>

      <div className="step-content">
        <div className="selection-header">
          <div className="selection-count">
            已选择 <strong>{selectedItems.length}</strong> / {copywritingList.length} 条文案
          </div>
          <button 
            type="button" 
            className="btn-link"
            onClick={handleSelectAll}
          >
            {selectedItems.length === copywritingList.length ? '取消全选' : '全选'}
          </button>
        </div>

        <div className="copywriting-list">
          {displayedList.map((item, index) => {
            const isExpanded = expandedItems[item.record_id]
            const text = item.fields['原文案'] || '（无文案内容）'
            const isLong = text.length > 100
            const displayText = isExpanded || !isLong ? text : text.substring(0, 100) + '...'
            
            return (
              <div 
                key={item.record_id}
                className={`copywriting-item ${selectedItems.includes(item.record_id) ? 'selected' : ''}`}
                onClick={() => handleSelectItem(item.record_id)}
              >
                <div className="item-checkbox">
                  <input 
                    type="checkbox"
                    checked={selectedItems.includes(item.record_id)}
                    onChange={() => {}}
                  />
                </div>
                <div className="item-content">
                  <div className="item-header">
                    <div className="item-number">#{index + 1}</div>
                    {item.fields['状态'] && (
                      <div className="item-status">{item.fields['状态']}</div>
                    )}
                  </div>
                  <div className="item-text">
                    {displayText}
                  </div>
                  {isLong && (
                    <button
                      className="btn-expand"
                      onClick={(e) => toggleExpand(item.record_id, e)}
                    >
                      {isExpanded ? '收起' : '展开全文'}
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {copywritingList.length > 2 && (
          <div className="show-more-container">
            <button
              type="button"
              className="btn-show-more"
              onClick={toggleShowAll}
            >
              {showAll ? (
                <>
                  <span>收起</span>
                  <span style={{ marginLeft: '8px' }}>▲</span>
                </>
              ) : (
                <>
                  <span>展开查看更多 ({hiddenCount} 条)</span>
                  <span style={{ marginLeft: '8px' }}>▼</span>
                </>
              )}
            </button>
          </div>
        )}

        {copywritingList.length === 0 && (
          <div className="empty-state">
            <p>😕 未找到文案数据</p>
            <p>请确保表格中有"原文案"列</p>
          </div>
        )}

        <div className="step-actions">
          <button type="button" className="btn-secondary" onClick={onBack}>
            上一步
          </button>
          <button 
            type="button" 
            className="btn-primary"
            onClick={handleSubmit}
            disabled={selectedItems.length === 0}
          >
            下一步（已选{selectedItems.length}条）
          </button>
        </div>
      </div>

      <div className="step-tips">
        <h4>提示</h4>
        <ul>
          <li>可以选择一条或多条文案进行批量处理</li>
          <li>建议先选择少量文案测试效果</li>
          <li>处理完成后会自动回写到飞书表格</li>
        </ul>
      </div>
    </div>
  )
}

export default StepSelectCopy
