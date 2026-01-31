import React from 'react'
import './WelcomePage.css'

function WelcomePage({ onStart }) {
  return (
    <div className="welcome-page">
      <div className="welcome-content">
        <div className="welcome-icon">🎬</div>
        <h1>批量自动剪辑智能体</h1>
        <p className="welcome-subtitle">
          从文案到视频，全流程智能化自动处理<br/>
          连接飞书 · 智能匹配 · 一键生成
        </p>
        
        <div className="btn-group">
          <button className="btn-start" onClick={onStart}>开始使用</button>
          <button className="btn-docs" onClick={() => alert('查看文档功能开发中...')}>查看文档</button>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>飞书集成</h3>
            <p>直接读取飞书多维表格文案，自动回写生成结果</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>智能处理</h3>
            <p>自动清洗文案、分镜拆解、关键词提取</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🎥</div>
            <h3>多源素材</h3>
            <p>本地素材库 + 网络搜索 + AI视频生成</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>批量处理</h3>
            <p>并行处理多个视频，自动上传云存储</p>
          </div>
        </div>

        <div className="workflow-section">
          <h3 className="workflow-title">工作流程</h3>
          <div className="workflow-steps">
            <div className="workflow-step">
              <div className="step-number">1</div>
              <div className="step-name">连接飞书</div>
              <div className="step-desc">配置飞书表格连接</div>
            </div>
            
            <div className="workflow-step">
              <div className="step-number">2</div>
              <div className="step-name">选择文案</div>
              <div className="step-desc">选择要处理的文案</div>
            </div>
            
            <div className="workflow-step">
              <div className="step-number">3</div>
              <div className="step-name">配置素材</div>
              <div className="step-desc">设置素材来源</div>
            </div>
            
            <div className="workflow-step">
              <div className="step-number">4</div>
              <div className="step-name">设置输出</div>
              <div className="step-desc">配置输出参数</div>
            </div>
            
            <div className="workflow-step">
              <div className="step-number">5</div>
              <div className="step-name">开始处理</div>
              <div className="step-desc">自动生成视频</div>
            </div>
          </div>
        </div>

        <div className="welcome-tips">
          <p>💡 首次使用需要登录并配置基本信息</p>
          <p>💡 配置信息将自动保存，下次使用无需重复配置</p>
          <p>💡 支持批量处理，自动上传云存储并回写飞书表格</p>
        </div>
      </div>
    </div>
  )
}

export default WelcomePage
