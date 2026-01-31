import React, { useState, useEffect } from 'react'
import './Steps.css'
import { getConfig, saveConfig, isRememberEnabled } from '../../utils/configMemory'

function StepOutput({ user, onComplete, onBack }) {
  const [config, setConfig] = useState({
    ossAccessKeyId: '',
    ossAccessKeySecret: '',
    ossBucketName: '',
    ossEndpoint: '',
    digitalHumanEnabled: false,
    heygenApiKey: ''
  })

  useEffect(() => {
    loadMemorizedConfig()
    loadSavedConfig()
  }, [user])

  const loadMemorizedConfig = () => {
    const memorized = getConfig('output')
    if (memorized) {
      setConfig(memorized)
    }
  }

  const loadSavedConfig = async () => {
    try {
      const response = await fetch('/api/user/config/output', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.config) {
          setConfig({ ...config, ...data.config })
        }
      }
    } catch (error) {
      console.log('使用默认配置')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // 测试模式：跳过验证
    const isTestMode = false
    
    if (isTestMode) {
      // 使用模拟配置
      onComplete({
        ...config,
        ossAccessKeyId: config.ossAccessKeyId || 'mock_oss_key',
        ossBucketName: config.ossBucketName || 'mock_bucket'
      })
      return
    }
    
    // 验证必填项
    if (!config.ossAccessKeyId || !config.ossBucketName) {
      alert('请填写云存储必填项')
      return
    }
    
    // 保存配置到服务器
    await fetch('/api/user/config/output', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify(config)
    })
    
    // 保存到本地记忆
    if (isRememberEnabled()) {
      saveConfig('output', config)
    }
    
    onComplete(config)
  }

  return (
    <div className="step-container">
      <div className="step-header">
        <h2>☁️ 步骤 4: 配置输出设置</h2>
        <p>设置视频输出和存储方式</p>
        <p style={{ fontSize: '0.9rem', color: '#667eea', marginTop: '0.5rem' }}>
          🧪 测试模式：可空白直接点击完成配置
        </p>
      </div>

      <div className="step-content">
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <h3>阿里云OSS配置</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Access Key ID <span className="required">*</span></label>
                <input
                  type="text"
                  value={config.ossAccessKeyId}
                  onChange={(e) => setConfig({ ...config, ossAccessKeyId: e.target.value })}
                  placeholder="LTAI...（测试模式可留空）"
                />
              </div>
              <div className="form-group">
                <label>Access Key Secret <span className="required">*</span></label>
                <input
                  type="password"
                  value={config.ossAccessKeySecret}
                  onChange={(e) => setConfig({ ...config, ossAccessKeySecret: e.target.value })}
                  placeholder="密钥Secret（测试模式可留空）"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Bucket Name <span className="required">*</span></label>
                <input
                  type="text"
                  value={config.ossBucketName}
                  onChange={(e) => setConfig({ ...config, ossBucketName: e.target.value })}
                  placeholder="my-video-bucket（测试模式可留空）"
                />
              </div>
              <div className="form-group">
                <label>Endpoint</label>
                <input
                  type="text"
                  value={config.ossEndpoint}
                  onChange={(e) => setConfig({ ...config, ossEndpoint: e.target.value })}
                  placeholder="oss-cn-hangzhou.aliyuncs.com"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>数字人配置（可选）</h3>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.digitalHumanEnabled}
                  onChange={(e) => setConfig({ ...config, digitalHumanEnabled: e.target.checked })}
                />
                <span>启用数字人功能</span>
              </label>
              <small>注意：HeyGen API调用会消耗积分</small>
            </div>
            {config.digitalHumanEnabled && (
              <div className="form-group">
                <label>HeyGen API Key</label>
                <input
                  type="text"
                  value={config.heygenApiKey}
                  onChange={(e) => setConfig({ ...config, heygenApiKey: e.target.value })}
                  placeholder="sk_..."
                />
              </div>
            )}
          </div>

          <div className="step-actions">
            <button type="button" className="btn-secondary" onClick={onBack}>
              上一步
            </button>
            <button type="submit" className="btn-primary">
              完成配置，开始处理
            </button>
          </div>
        </form>
      </div>

      <div className="step-tips">
        <h4>提示</h4>
        <ul>
          <li>视频生成后会自动上传到OSS</li>
          <li>上传链接会自动回写到飞书表格</li>
          <li>数字人功能可选，建议先测试效果</li>
          <li>配置将保存，下次使用无需重填</li>
        </ul>
      </div>
    </div>
  )
}

export default StepOutput
