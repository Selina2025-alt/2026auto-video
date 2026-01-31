import React, { useState, useEffect } from 'react'
import './Steps.css'
import FirstTimeNotice from '../FirstTimeNotice'
import { getConfig, saveConfig, shouldAskRemember, confirmRemember, isRememberEnabled } from '../../utils/configMemory'

function StepFeishu({ user, onComplete, onBack }) {
  const [feishuUrl, setFeishuUrl] = useState('')
  const [appId, setAppId] = useState('')
  const [appSecret, setAppSecret] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [savedConfig, setSavedConfig] = useState(null)
  const [showRememberNotice, setShowRememberNotice] = useState(false)

  useEffect(() => {
    // 加载本地记忆的配置
    loadMemorizedConfig()
    // 也尝试加载服务器配置作为备份
    loadSavedConfig()
  }, [user])

  const loadMemorizedConfig = () => {
    const config = getConfig('feishu')
    if (config) {
      setFeishuUrl(config.feishuUrl || '')
      setAppId(config.appId || '')
      setAppSecret(config.appSecret || '')
      setSavedConfig(config)
    }
  }

  const loadSavedConfig = async () => {
    try {
      const response = await fetch('/api/user/config/feishu', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.config) {
          setSavedConfig(data.config)
          setAppId(data.config.appId || '')
          setAppSecret(data.config.appSecret || '')
        }
      }
    } catch (error) {
      console.log('未找到已保存的配置')
    }
  }

  const parseFeishuUrl = (url) => {
    try {
      // 解析飞书多维表格链接
      // 示例: https://xxx.feishu.cn/base/IV5db39jZaL20zsZPsZcviVxnuc?table=tblRClgvIVXxE4e7
      const urlObj = new URL(url)
      const pathParts = urlObj.pathname.split('/')
      const baseToken = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2]
      const tableId = urlObj.searchParams.get('table')
      
      if (!baseToken || !tableId) {
        throw new Error('无效的飞书表格链接')
      }
      
      return { baseToken, tableId }
    } catch (error) {
      throw new Error('链接格式不正确，请检查后重试')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // 测试模式：跳过验证，使用模拟数据
    const isTestMode = false
    
    if (isTestMode) {
      setTimeout(() => {
        // 模拟文案数据
        const mockCopywriting = [
          { record_id: '1', fields: { '原文案': '这是第一条测试文案，用于展示视频生成效果。包含了多个句子和丰富的内容描述。', '状态': '待处理' } },
          { record_id: '2', fields: { '原文案': '第二条文案示例，讲述一个有趣的故事。从前有座山，山里有座庙。', '状态': '待处理' } },
          { record_id: '3', fields: { '原文案': '第三条文案，介绍产品特性和功能亮点。我们的产品功能强大，操作简单。', '状态': '待处理' } },
          { record_id: '4', fields: { '原文案': '第四条文案，分享用户评价和使用体验。用户反馈非常积极正面。' } },
          { record_id: '5', fields: { '原文案': '第五条文案，展示技术创新和未来展望。科技改变生活，创新驱动未来。' } }
        ]
        
        onComplete({
          baseToken: 'mock_base_token',
          tableId: 'mock_table_id',
          appId: feishuUrl || 'mock_app_id',
          appSecret: 'mock_secret',
          copywritingList: mockCopywriting
        })
        setLoading(false)
      }, 800)
      return
    }

    try {
      // 解析飞书链接
      const { baseToken, tableId } = parseFeishuUrl(feishuUrl)

      // 保存配置到后端
      const saveResponse = await fetch('/api/user/config/feishu', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          appId,
          appSecret,
          baseToken,
          tableId
        })
      })

      if (!saveResponse.ok) {
        throw new Error('保存配置失败')
      }

      // 测试连接并读取表格
      const testResponse = await fetch('/api/feishu/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          appId,
          appSecret,
          baseToken,
          tableId
        })
      })

      const testData = await testResponse.json()

      if (testResponse.ok) {
        // 询问用户是否记住配置（仅首次）
        if (shouldAskRemember()) {
          setShowRememberNotice(true)
          // 暂存数据，等用户确认后再继续
          window._pendingFeishuData = {
            baseToken,
            tableId,
            appId,
            appSecret,
            feishuUrl,
            copywritingList: testData.copywritingList || []
          }
        } else {
          // 已经设置过，直接保存并继续
          if (isRememberEnabled()) {
            saveConfig('feishu', {
              feishuUrl,
              appId,
              appSecret,
              baseToken,
              tableId
            })
          }
          
          onComplete({
            baseToken,
            tableId,
            appId,
            appSecret,
            copywritingList: testData.copywritingList || []
          })
        }
      } else {
        setError(testData.message || '连接失败，请检查配置')
      }
    } catch (error) {
      setError(error.message || '连接失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handleUseSaved = () => {
    if (savedConfig) {
      setAppId(savedConfig.appId)
      setAppSecret(savedConfig.appSecret)
      if (savedConfig.lastUrl) {
        setFeishuUrl(savedConfig.lastUrl)
      }
    }
  }

  const handleRememberConfirm = () => {
    confirmRemember(true)
    const data = window._pendingFeishuData
    if (data) {
      saveConfig('feishu', {
        feishuUrl: data.feishuUrl,
        appId: data.appId,
        appSecret: data.appSecret,
        baseToken: data.baseToken,
        tableId: data.tableId
      })
      onComplete({
        baseToken: data.baseToken,
        tableId: data.tableId,
        appId: data.appId,
        appSecret: data.appSecret,
        copywritingList: data.copywritingList
      })
      window._pendingFeishuData = null
    }
    setShowRememberNotice(false)
  }

  const handleRememberCancel = () => {
    confirmRemember(false)
    const data = window._pendingFeishuData
    if (data) {
      onComplete({
        baseToken: data.baseToken,
        tableId: data.tableId,
        appId: data.appId,
        appSecret: data.appSecret,
        copywritingList: data.copywritingList
      })
      window._pendingFeishuData = null
    }
    setShowRememberNotice(false)
  }

  return (
    <>
      {showRememberNotice && (
        <FirstTimeNotice 
          onConfirm={handleRememberConfirm}
          onCancel={handleRememberCancel}
        />
      )}
    <div className="step-container">
      <div className="step-header">
        <h2>📊 步骤 1: 连接飞书多维表格</h2>
        <p>输入飞书多维表格链接和API凭证</p>
        <p style={{ fontSize: '0.9rem', color: '#667eea', marginTop: '0.5rem' }}>
          🧪 测试模式：可空白直接点击下一步
        </p>
      </div>

      <div className="step-content">
        {savedConfig && (
          <div className="saved-config-notice">
            <p>✓ 检测到已保存的配置</p>
            <button className="btn-link" onClick={handleUseSaved}>
              使用上次的配置
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="step-form">
          {error && (
            <div className="error-box">
              ⚠️ {error}
            </div>
          )}

          <div className="form-section">
            <h3>飞书多维表格链接</h3>
            <div className="form-group">
              <label>表格链接 <span className="required">*</span></label>
              <input
                  type="text"
                  value={feishuUrl}
                  onChange={(e) => setFeishuUrl(e.target.value)}
                  placeholder="https://xxx.feishu.cn/base/xxxxx?table=xxxxx（测试模式可留空）"
              />
              <small>粘贴飞书多维表格的完整URL，系统将自动解析Base Token和Table ID</small>
            </div>
          </div>

          <div className="form-section">
            <h3>飞书API凭证</h3>
            <div className="form-row">
              <div className="form-group">
                <label>App ID <span className="required">*</span></label>
                <input
                  type="text"
                  value={appId}
                  onChange={(e) => setAppId(e.target.value)}
                  placeholder="cli_xxxxxxxxxxxxx（测试模式可留空）"
                />
              </div>
              <div className="form-group">
                <label>App Secret <span className="required">*</span></label>
                <input
                  type="password"
                  value={appSecret}
                  onChange={(e) => setAppSecret(e.target.value)}
                  placeholder="输入App Secret（测试模式可留空）"
                />
              </div>
            </div>
            <small className="help-text">
              💡 如何获取：登录飞书开放平台 → 创建应用 → 获取凭证
            </small>
          </div>

          <div className="step-actions">
            {onBack && (
              <button 
                type="button" 
                className="btn-secondary"
                onClick={onBack}
              >
                ← 返回上一步
              </button>
            )}
            <button 
              type="submit" 
              className="btn-primary"
              disabled={loading}
            >
              {loading ? '连接中...' : '连接并读取文案'}
            </button>
          </div>
        </form>
      </div>

      <div className="step-tips">
        <h4>💡 提示</h4>
        <ul>
          <li>确保飞书应用有读取多维表格的权限</li>
          <li>表格中需要包含"原文案"列</li>
          {isRememberEnabled() ? (
            <li>✓ 配置已启用记忆，将自动保存</li>
          ) : (
            <li>首次使用时将询问是否记住配置</li>
          )}
        </ul>
      </div>
    </div>
    </>
  )
}

export default StepFeishu
