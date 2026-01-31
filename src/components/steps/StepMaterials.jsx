import React, { useState, useEffect } from 'react'
import './Steps.css'
import { getConfig, saveConfig, isRememberEnabled } from '../../utils/configMemory'

function StepMaterials({ user, onComplete, onBack }) {
  const [config, setConfig] = useState({
    localPath: './local_materials',
    useLocalMaterials: true,
    useWebSearch: true,
    materialApis: {
      pexels: '',
      freepik: '',
      coverr: '',
      firecrawl: ''
    },
    aiVideoMode: 'skip', // tool, proxy, skip
    aiVideoTools: [],
    aiVideoProxy: {
      baseUrl: '',
      apiKey: ''
    }
  })

  useEffect(() => {
    loadMemorizedConfig()
    loadSavedConfig()
  }, [user])

  const loadMemorizedConfig = () => {
    const memorized = getConfig('materials')
    if (memorized) {
      setConfig(memorized)
    }
  }

  const loadSavedConfig = async () => {
    try {
      const response = await fetch('/api/user/config/materials', {
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
    
    // 保存配置到服务器
    await fetch('/api/user/config/materials', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify(config)
    })
    
    // 保存到本地记忆
    if (isRememberEnabled()) {
      saveConfig('materials', config)
    }
    
    onComplete(config)
  }

  const handleSkip = () => {
    // 保存到本地记忆
    if (isRememberEnabled()) {
      saveConfig('materials', config)
    }
    // 使用默认配置跳过
    onComplete(config)
  }

  const addAiTool = () => {
    setConfig({
      ...config,
      aiVideoTools: [...config.aiVideoTools, { name: '', apiKey: '' }]
    })
  }

  const updateAiTool = (index, field, value) => {
    const newTools = [...config.aiVideoTools]
    newTools[index][field] = value
    setConfig({ ...config, aiVideoTools: newTools })
  }

  const removeAiTool = (index) => {
    setConfig({
      ...config,
      aiVideoTools: config.aiVideoTools.filter((_, i) => i !== index)
    })
  }

  return (
    <div className="step-container">
      <div className="step-header">
        <h2>🎥 步骤 3: 配置素材来源</h2>
        <p>设置视频素材的获取方式（可跳过使用默认配置）</p>
        <p style={{ fontSize: '0.9rem', color: '#667eea', marginTop: '0.5rem' }}>
          🧪 测试模式：可直接跳过或保存并继续
        </p>
      </div>

      <div className="step-content">
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <h3>本地素材库</h3>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.useLocalMaterials}
                  onChange={(e) => setConfig({ ...config, useLocalMaterials: e.target.checked })}
                />
                <span>启用本地素材库（优先级最高）</span>
              </label>
            </div>
            {config.useLocalMaterials && (
              <div className="form-group">
                <label>素材库路径</label>
                <input
                  type="text"
                  value={config.localPath}
                  onChange={(e) => setConfig({ ...config, localPath: e.target.value })}
                  placeholder="./local_materials"
                />
                <small>存放本地视频素材的目录</small>
              </div>
            )}
          </div>

          <div className="form-section">
            <h3>网络素材搜索（可选）</h3>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.useWebSearch}
                  onChange={(e) => setConfig({ ...config, useWebSearch: e.target.checked })}
                />
                <span>启用网络素材搜索</span>
              </label>
            </div>
            {config.useWebSearch && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label>Pexels API Key</label>
                    <input
                      type="text"
                      value={config.materialApis.pexels}
                      onChange={(e) => setConfig({
                        ...config,
                        materialApis: { ...config.materialApis, pexels: e.target.value }
                      })}
                      placeholder="可选"
                    />
                  </div>
                  <div className="form-group">
                    <label>Freepik API Key</label>
                    <input
                      type="text"
                      value={config.materialApis.freepik}
                      onChange={(e) => setConfig({
                        ...config,
                        materialApis: { ...config.materialApis, freepik: e.target.value }
                      })}
                      placeholder="可选"
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Coverr API Key</label>
                    <input
                      type="text"
                      value={config.materialApis.coverr}
                      onChange={(e) => setConfig({
                        ...config,
                        materialApis: { ...config.materialApis, coverr: e.target.value }
                      })}
                      placeholder="可选"
                    />
                  </div>
                  <div className="form-group">
                    <label>Firecrawl API Key</label>
                    <input
                      type="text"
                      value={config.materialApis.firecrawl}
                      onChange={(e) => setConfig({
                        ...config,
                        materialApis: { ...config.materialApis, firecrawl: e.target.value }
                      })}
                      placeholder="可选"
                    />
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="form-section">
            <h3>AI视频生成（可选）</h3>
            <div className="radio-group">
              <label className="radio-label">
                <input
                  type="radio"
                  name="aiMode"
                  value="skip"
                  checked={config.aiVideoMode === 'skip'}
                  onChange={(e) => setConfig({ ...config, aiVideoMode: e.target.value })}
                />
                <span>跳过AI生成（仅使用本地+网络素材）</span>
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  name="aiMode"
                  value="tool"
                  checked={config.aiVideoMode === 'tool'}
                  onChange={(e) => setConfig({ ...config, aiVideoMode: e.target.value })}
                />
                <span>使用AI视频生成工具</span>
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  name="aiMode"
                  value="proxy"
                  checked={config.aiVideoMode === 'proxy'}
                  onChange={(e) => setConfig({ ...config, aiVideoMode: e.target.value })}
                />
                <span>使用中转站API</span>
              </label>
            </div>

            {config.aiVideoMode === 'tool' && (
              <div className="ai-tools-config">
                <p style={{ fontSize: '0.9rem', color: '#5D4E37', marginBottom: '1rem' }}>
                  支持的AI工具：Runway ML, Pika Labs, Stable Video, 可灵AI (Kling)
                </p>
                {config.aiVideoTools.map((tool, index) => (
                  <div key={index} className="ai-tool-row">
                    <select
                      value={tool.name}
                      onChange={(e) => updateAiTool(index, 'name', e.target.value)}
                      style={{ flex: 1, padding: '0.75rem', borderRadius: '12px', border: '2px solid #FFD700' }}
                    >
                      <option value="">选择AI工具</option>
                      <option value="runway">Runway ML</option>
                      <option value="pika">Pika Labs</option>
                      <option value="stable_video">Stable Video Diffusion</option>
                      <option value="kling">可灵AI (Kling)</option>
                    </select>
                    <input
                      type="text"
                      value={tool.apiKey}
                      onChange={(e) => updateAiTool(index, 'apiKey', e.target.value)}
                      placeholder="API密钥"
                      style={{ flex: 2 }}
                    />
                    <button 
                      type="button" 
                      onClick={() => removeAiTool(index)}
                      style={{ 
                        padding: '0.75rem 1.5rem',
                        backgroundColor: '#FF5722',
                        color: 'white',
                        border: 'none',
                        borderRadius: '12px',
                        cursor: 'pointer'
                      }}
                    >
                      删除
                    </button>
                  </div>
                ))}
                <button type="button" className="btn-link" onClick={addAiTool}>
                  + 添加AI工具
                </button>
              </div>
            )}

            {config.aiVideoMode === 'proxy' && (
              <div className="form-row">
                <div className="form-group">
                  <label>Base URL</label>
                  <input
                    type="text"
                    value={config.aiVideoProxy.baseUrl}
                    onChange={(e) => setConfig({
                      ...config,
                      aiVideoProxy: { ...config.aiVideoProxy, baseUrl: e.target.value }
                    })}
                    placeholder="https://api.example.com"
                  />
                </div>
                <div className="form-group">
                  <label>API Key</label>
                  <input
                    type="text"
                    value={config.aiVideoProxy.apiKey}
                    onChange={(e) => setConfig({
                      ...config,
                      aiVideoProxy: { ...config.aiVideoProxy, apiKey: e.target.value }
                    })}
                    placeholder="输入API密钥"
                  />
                </div>
              </div>
            )}
          </div>

          <div className="step-actions">
            <button type="button" className="btn-secondary" onClick={onBack}>
              上一步
            </button>
            <button type="button" className="btn-link" onClick={handleSkip}>
              跳过此步骤
            </button>
            <button type="submit" className="btn-primary">
              保存并继续
            </button>
          </div>
        </form>
      </div>

      <div className="step-tips">
        <h4>素材匹配优先级</h4>
        <ul>
          <li>优先使用本地素材库（最快、最省钱）</li>
          <li>本地无匹配则搜索网络素材</li>
          <li>仍无合适素材才使用AI生成</li>
          <li>可跳过此步骤使用默认配置</li>
        </ul>
      </div>
    </div>
  )
}

export default StepMaterials
