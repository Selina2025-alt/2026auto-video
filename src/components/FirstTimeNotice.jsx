import React, { useState, useEffect } from 'react'
import './FirstTimeNotice.css'

function FirstTimeNotice({ onClose, onOpenSettings }) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // 延迟显示动画
    setTimeout(() => setIsVisible(true), 100)
  }, [])

  const handleClose = () => {
    setIsVisible(false)
    setTimeout(() => onClose(), 300)
  }

  const handleGetStarted = () => {
    handleClose()
    setTimeout(() => onOpenSettings(), 350)
  }

  return (
    <div className={`first-time-notice-overlay ${isVisible ? 'visible' : ''}`}>
      <div className={`first-time-notice ${isVisible ? 'visible' : ''}`}>
        <div className="notice-header">
          <div className="notice-icon">👋</div>
          <h1>欢迎使用批量自动剪辑智能体</h1>
        </div>

        <div className="notice-content">
          <p className="notice-intro">
            这是您第一次使用本系统，需要完成一些基本配置才能开始使用。
          </p>

          <div className="feature-list">
            <div className="feature-item">
              <span className="feature-icon">📊</span>
              <div className="feature-text">
                <h3>飞书表格集成</h3>
                <p>连接飞书多维表格，自动读取文案并回写视频链接</p>
              </div>
            </div>

            <div className="feature-item">
              <span className="feature-icon">🎬</span>
              <div className="feature-text">
                <h3>智能素材匹配</h3>
                <p>自动从本地或网络搜索匹配视频素材</p>
              </div>
            </div>

            <div className="feature-item">
              <span className="feature-icon">🎙️</span>
              <div className="feature-text">
                <h3>AI配音生成</h3>
                <p>使用Edge TTS生成自然流畅的语音</p>
              </div>
            </div>

            <div className="feature-item">
              <span className="feature-icon">☁️</span>
              <div className="feature-text">
                <h3>云存储上传</h3>
                <p>自动上传视频到阿里云OSS并分享</p>
              </div>
            </div>
          </div>

          <div className="notice-steps">
            <h3>快速开始步骤</h3>
            <ol>
              <li>点击下方「开始配置」按钮</li>
              <li>填写飞书应用配置信息</li>
              <li>（可选）配置素材库和OSS</li>
              <li>保存配置并开始使用</li>
            </ol>
          </div>
        </div>

        <div className="notice-actions">
          <button className="btn-primary" onClick={handleGetStarted}>
            开始配置 →
          </button>
        </div>
      </div>
    </div>
  )
}

export default FirstTimeNotice
