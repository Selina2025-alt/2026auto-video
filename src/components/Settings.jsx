import React, { useState, useEffect } from 'react'
import './Settings.css'

function Settings({ user, onLogout, onBack }) {
  const [settings, setSettings] = useState({
    feishu: {
      appId: '',
      appSecret: '',
      baseToken: '',
      tableId: ''
    },
    materials: {
      localPath: './local_materials',
      pexelsApiKey: '',
      freepikApiKey: '',
      coverrApiKey: ''
    },
    output: {
      voice: 'female',
      bgmPath: '',
      ossAccessKeyId: '',
      ossAccessKeySecret: '',
      ossBucketName: '',
      ossEndpoint: ''
    }
  })

  const [saveStatus, setSaveStatus] = useState('')
  const [showSecrets, setShowSecrets] = useState({})

  useEffect(() => {
    // 加载保存的配置
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      // 加载各类配置
      const [feishuRes, materialsRes, outputRes] = await Promise.all([
        fetch('/api/user/config/feishu', { credentials: 'include' }),
        fetch('/api/user/config/materials', { credentials: 'include' }),
        fetch('/api/user/config/output', { credentials: 'include' })
      ])

      if (feishuRes.ok) {
        const data = await feishuRes.json()
        if (data.config) {
          setSettings(prev => ({ ...prev, feishu: { ...prev.feishu, ...data.config } }))
        }
      }

      if (materialsRes.ok) {
        const data = await materialsRes.json()
        if (data.config) {
          setSettings(prev => ({ ...prev, materials: { ...prev.materials, ...data.config } }))
        }
      }

      if (outputRes.ok) {
        const data = await outputRes.json()
        if (data.config) {
          setSettings(prev => ({ ...prev, output: { ...prev.output, ...data.config } }))
        }
      }
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }

  const handleSave = async () => {
    setSaveStatus('saving')
    try {
      // 分别保存各类配置
      const [feishuRes, materialsRes, outputRes] = await Promise.all([
        fetch('/api/user/config/feishu', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(settings.feishu)
        }),
        fetch('/api/user/config/materials', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(settings.materials)
        }),
        fetch('/api/user/config/output', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(settings.output)
        })
      ])

      if (feishuRes.ok && materialsRes.ok && outputRes.ok) {
        setSaveStatus('success')
        setTimeout(() => setSaveStatus(''), 2000)
      } else {
        setSaveStatus('error')
      }
    } catch (error) {
      console.error('保存配置失败:', error)
      setSaveStatus('error')
    }
  }

  const toggleSecretVisibility = (field) => {
    setShowSecrets(prev => ({
      ...prev,
      [field]: !prev[field]
    }))
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <button className="btn-back" onClick={onBack}>
          ← 返回
        </button>
        <h1>⚙️ 系统设置</h1>
        <div className="header-actions">
          <button className="btn-logout" onClick={onLogout}>
            退出登录
          </button>
        </div>
      </div>

      <div className="settings-content">
        {/* 飞书配置 */}
        <section className="settings-section">
          <h2>📊 飞书配置</h2>
          <div className="settings-fields">
            <div className="field-group">
              <label>应用 ID (App ID)</label>
              <input
                type="text"
                value={settings.feishu.appId}
                onChange={(e) => setSettings({
                  ...settings,
                  feishu: { ...settings.feishu, appId: e.target.value }
                })}
                placeholder="cli_xxxxxxxxxxxxx"
              />
            </div>
            <div className="field-group">
              <label>应用密钥 (App Secret)</label>
              <div className="secret-input">
                <input
                  type={showSecrets.appSecret ? 'text' : 'password'}
                  value={settings.feishu.appSecret}
                  onChange={(e) => setSettings({
                    ...settings,
                    feishu: { ...settings.feishu, appSecret: e.target.value }
                  })}
                  placeholder="xxxxxxxxxxxxxxxxxxxx"
                />
                <button
                  type="button"
                  className="btn-toggle-visibility"
                  onClick={() => toggleSecretVisibility('appSecret')}
                >
                  {showSecrets.appSecret ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
            <div className="field-group">
              <label>多维表格 Base Token</label>
              <input
                type="text"
                value={settings.feishu.baseToken}
                onChange={(e) => setSettings({
                  ...settings,
                  feishu: { ...settings.feishu, baseToken: e.target.value }
                })}
                placeholder="bascnxxxxxxxxxxxxxx"
              />
            </div>
            <div className="field-group">
              <label>表格 ID (Table ID)</label>
              <input
                type="text"
                value={settings.feishu.tableId}
                onChange={(e) => setSettings({
                  ...settings,
                  feishu: { ...settings.feishu, tableId: e.target.value }
                })}
                placeholder="tblxxxxxxxxxxxxxx"
              />
            </div>
          </div>
        </section>

        {/* 素材配置 */}
        <section className="settings-section">
          <h2>🎬 素材配置</h2>
          <div className="settings-fields">
            <div className="field-group">
              <label>本地素材路径</label>
              <input
                type="text"
                value={settings.materials.localPath}
                onChange={(e) => setSettings({
                  ...settings,
                  materials: { ...settings.materials, localPath: e.target.value }
                })}
                placeholder="./local_materials"
              />
              <p className="field-hint">本地素材文件夹路径，用于优先匹配视频素材</p>
            </div>
            <div className="field-group">
              <label>Pexels API Key</label>
              <div className="secret-input">
                <input
                  type={showSecrets.pexelsApiKey ? 'text' : 'password'}
                  value={settings.materials.pexelsApiKey}
                  onChange={(e) => setSettings({
                    ...settings,
                    materials: { ...settings.materials, pexelsApiKey: e.target.value }
                  })}
                  placeholder="xxxxxxxxxxxxxxxxxxxx"
                />
                <button
                  type="button"
                  className="btn-toggle-visibility"
                  onClick={() => toggleSecretVisibility('pexelsApiKey')}
                >
                  {showSecrets.pexelsApiKey ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
            <div className="field-group">
              <label>Freepik API Key</label>
              <div className="secret-input">
                <input
                  type={showSecrets.freepikApiKey ? 'text' : 'password'}
                  value={settings.materials.freepikApiKey}
                  onChange={(e) => setSettings({
                    ...settings,
                    materials: { ...settings.materials, freepikApiKey: e.target.value }
                  })}
                  placeholder="xxxxxxxxxxxxxxxxxxxx"
                />
                <button
                  type="button"
                  className="btn-toggle-visibility"
                  onClick={() => toggleSecretVisibility('freepikApiKey')}
                >
                  {showSecrets.freepikApiKey ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* 输出配置 */}
        <section className="settings-section">
          <h2>🎥 输出配置</h2>
          <div className="settings-fields">
            <div className="field-group">
              <label>语音类型</label>
              <select
                value={settings.output.voice}
                onChange={(e) => setSettings({
                  ...settings,
                  output: { ...settings.output, voice: e.target.value }
                })}
              >
                <option value="female">女声 (晓晓)</option>
                <option value="male">男声 (云扬)</option>
                <option value="female2">女声 (晓伊)</option>
                <option value="male2">男声 (云希)</option>
              </select>
            </div>
            <div className="field-group">
              <label>背景音乐路径</label>
              <input
                type="text"
                value={settings.output.bgmPath}
                onChange={(e) => setSettings({
                  ...settings,
                  output: { ...settings.output, bgmPath: e.target.value }
                })}
                placeholder="./bgm/music.mp3"
              />
              <p className="field-hint">可选：为视频添加背景音乐</p>
            </div>
          </div>
        </section>

        {/* OSS 配置 */}
        <section className="settings-section">
          <h2>☁️ 阿里云 OSS 配置</h2>
          <div className="settings-fields">
            <div className="field-group">
              <label>Access Key ID</label>
              <div className="secret-input">
                <input
                  type={showSecrets.ossAccessKeyId ? 'text' : 'password'}
                  value={settings.output.ossAccessKeyId}
                  onChange={(e) => setSettings({
                    ...settings,
                    output: { ...settings.output, ossAccessKeyId: e.target.value }
                  })}
                  placeholder="LTAI5txxxxxxxxxxxxxxx"
                />
                <button
                  type="button"
                  className="btn-toggle-visibility"
                  onClick={() => toggleSecretVisibility('ossAccessKeyId')}
                >
                  {showSecrets.ossAccessKeyId ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
            <div className="field-group">
              <label>Access Key Secret</label>
              <div className="secret-input">
                <input
                  type={showSecrets.ossAccessKeySecret ? 'text' : 'password'}
                  value={settings.output.ossAccessKeySecret}
                  onChange={(e) => setSettings({
                    ...settings,
                    output: { ...settings.output, ossAccessKeySecret: e.target.value }
                  })}
                  placeholder="xxxxxxxxxxxxxxxxxxxx"
                />
                <button
                  type="button"
                  className="btn-toggle-visibility"
                  onClick={() => toggleSecretVisibility('ossAccessKeySecret')}
                >
                  {showSecrets.ossAccessKeySecret ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
            <div className="field-group">
              <label>Bucket 名称</label>
              <input
                type="text"
                value={settings.output.ossBucketName}
                onChange={(e) => setSettings({
                  ...settings,
                  output: { ...settings.output, ossBucketName: e.target.value }
                })}
                placeholder="my-bucket"
              />
            </div>
            <div className="field-group">
              <label>Endpoint</label>
              <input
                type="text"
                value={settings.output.ossEndpoint}
                onChange={(e) => setSettings({
                  ...settings,
                  output: { ...settings.output, ossEndpoint: e.target.value }
                })}
                placeholder="oss-cn-hangzhou.aliyuncs.com"
              />
              <p className="field-hint">不包含 https:// 前缀</p>
            </div>
          </div>
        </section>

        {/* 保存按钮 */}
        <div className="settings-actions">
          <button
            className={`btn-save ${saveStatus}`}
            onClick={handleSave}
            disabled={saveStatus === 'saving'}
          >
            {saveStatus === 'saving' ? '保存中...' :
             saveStatus === 'success' ? '✓ 已保存' :
             saveStatus === 'error' ? '✗ 保存失败' :
             '保存配置'}
          </button>
        </div>

        {/* 帮助信息 */}
        <div className="settings-help">
          <h3>📖 配置说明</h3>
          <details>
            <summary>如何获取飞书配置？</summary>
            <ol>
              <li>访问 <a href="https://open.feishu.cn/app" target="_blank" rel="noopener noreferrer">飞书开放平台</a></li>
              <li>创建企业自建应用</li>
              <li>在「凭证与基础信息」页面获取 App ID 和 App Secret</li>
              <li>在「权限管理」中开通以下权限：
                <ul>
                  <li>bitable:app - 读取和写入多维表格</li>
                  <li>bitable:app:readonly - 读取多维表格</li>
                </ul>
              </li>
              <li>打开飞书表格，从 URL 中获取 baseToken 和 tableId</li>
            </ol>
          </details>
          <details>
            <summary>如何获取 Pexels API Key？</summary>
            <ol>
              <li>访问 <a href="https://www.pexels.com/api/" target="_blank" rel="noopener noreferrer">Pexels API</a></li>
              <li>注册并创建新应用</li>
              <li>获取 API Key（免费）</li>
            </ol>
          </details>
        </div>
      </div>
    </div>
  )
}

export default Settings
