import React, { useState, useEffect, useRef } from 'react'
import './ProcessingPage.css'

function ProcessingPage({ sessionData }) {
  const [logs, setLogs] = useState([])
  const [isProcessing, setIsProcessing] = useState(true)
  const [completedVideos, setCompletedVideos] = useState([])
  const [currentStep, setCurrentStep] = useState('')
  const [stepDetails, setStepDetails] = useState({})
  const [allCompleted, setAllCompleted] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const wsRef = useRef(null)
  const logsEndRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  useEffect(() => {
    // 连接WebSocket
    connectWebSocket()
    // 开始处理
    startProcessing()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  useEffect(() => {
    // 自动滚动到最新日志
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8001/ws')

      ws.onopen = () => {
        addLog('✓ WebSocket连接已建立', 'success')
        reconnectAttempts.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        } catch (error) {
          console.log('收到消息:', event.data)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket连接已关闭')
        // 尝试重连
        if (isProcessing && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++
          addLog(`尝试重新连接 (${reconnectAttempts.current}/${maxReconnectAttempts})...`, 'warning')
          setTimeout(() => {
            connectWebSocket()
          }, 2000)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      addLog('WebSocket连接失败，将使用轮询模式获取进度', 'warning')
      startPolling()
    }
  }

  const startPolling = () => {
    // 如果WebSocket失败，使用轮询获取进度
    const pollInterval = setInterval(async () => {
      if (!isProcessing) {
        clearInterval(pollInterval)
        return
      }

      try {
        const response = await fetch('/api/process/status', {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          if (data.progress) {
            updateProgress(data.progress)
          }
          if (data.logs) {
            data.logs.forEach(log => addLog(log.message, log.level))
          }
        }
      } catch (error) {
        console.error('轮询失败:', error)
      }
    }, 2000)
  }

  const handleWebSocketMessage = (data) => {
    // 处理日志消息
    if (data.type === 'log') {
      addLog(data.message, data.level || 'info')

      // 如果是完成消息
      if (data.completed) {
        setIsProcessing(false)
        setAllCompleted(true)
        setShowResults(true)
        setCurrentStep('🎉 全部完成')
        setStepDetails({ progress: 100 })
      }
    }
    // 处理步骤更新
    else if (data.type === 'step') {
      if (data.step_name) {
        setCurrentStep(data.step_name)
      }
      if (data.details) {
        setStepDetails(data.details)
      }
      addLog(data.message, 'info')
    }
    // 处理旧格式的progress消息（兼容）
    else if (data.type === 'progress') {
      if (data.step) {
        setCurrentStep(data.step)
      }
      if (data.details) {
        setStepDetails(prev => ({ ...prev, ...data.details }))
      }
      addLog(data.message)
    }
    // 处理单个视频完成
    else if (data.type === 'video_completed') {
      if (data.video) {
        handleVideoCompleted(data.video)
        addLog(`✅ 视频 #${data.video.index} 已生成`, 'success')
      }
    }
    // 处理全部完成
    else if (data.type === 'all_completed') {
      setIsProcessing(false)
      setAllCompleted(true)
      setShowResults(true)
      setCurrentStep('🎉 全部完成')
      setStepDetails({ progress: 100 })
      addLog(`🎊 恭喜！共完成 ${data.total} 个视频！`, 'success')
    }
    // 处理旧格式的completed消息（兼容）
    else if (data.type === 'completed') {
      if (data.video) {
        handleVideoCompleted(data.video)
      }
    }
    // 处理旧格式的finished消息（兼容）
    else if (data.type === 'finished') {
      setIsProcessing(false)
      setAllCompleted(true)
      setShowResults(true)
      setCurrentStep('🎉 全部完成')
      setStepDetails({ progress: 100 })
      addLog('✅ 全部处理完成！', 'success')
    }
    // 处理错误
    else if (data.type === 'error') {
      addLog(data.error || data.message, 'error')
    }
  }

  const startProcessing = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/process/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(sessionData)
      })

      if (!response.ok) {
        throw new Error('启动处理失败')
      }

      addLog('🚀 开始处理视频...', 'info')
    } catch (error) {
      addLog(`错误: ${error.message}`, 'error')
      setIsProcessing(false)
    }
  }

  const addLog = (message, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString('zh-CN')
    setLogs(prev => [...prev, { time: timestamp, message, level }])
  }

  const handleVideoCompleted = (video) => {
    setCompletedVideos(prev => [...prev, video])
  }

  // 打开视频文件夹（仅本地文件）
  const openVideoFolder = (video) => {
    if (video.is_local && video.url) {
      const localPath = video.url.replace('file://', '')
      addLog(`本地视频路径: ${localPath}`, 'info')
      // 在Windows上可以尝试打开文件夹
      // 注意：这需要后端支持，目前仅显示路径
    }
  }

  // 切换结果显示
  const toggleResults = () => {
    setShowResults(!showResults)
  }

  // 重新开始
  const handleRestart = () => {
    setCompletedVideos([])
    setLogs([])
    setIsProcessing(true)
    setAllCompleted(false)
    setShowResults(false)
    setCurrentStep('')
    setStepDetails({})
    startProcessing()
  }

  return (
    <div className="processing-page">
      <div className="processing-header">
        <h2>⚙️ 正在处理视频</h2>
        <p>共 {sessionData.selectedCopywriting.length} 条文案</p>
        {allCompleted && (
          <button className="btn-toggle-results" onClick={toggleResults}>
            {showResults ? '隐藏结果' : '查看结果'}
          </button>
        )}
      </div>

      <div className="processing-content">
        {/* 当前步骤显示 */}
        {currentStep && (
          <div className="current-step-banner">
            <div className="step-icon">
              {isProcessing ? '🔄' : '✅'}
            </div>
            <div className="step-info">
              <div className="step-label">
                {isProcessing ? '正在处理' : '处理完成'}
              </div>
              <div className="step-name">{currentStep}</div>
              {stepDetails.progress !== undefined && (
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div
                      className="step-progress-fill"
                      style={{ width: `${stepDetails.progress}%` }}
                    />
                  </div>
                  <span className="step-progress-text">
                    总进度 {stepDetails.progress}%
                  </span>
                </div>
              )}
            </div>
            {isProcessing && (
              <div className="step-spinner">
                <div className="spinner"></div>
                <div className="spinner-text">处理中...</div>
              </div>
            )}
          </div>
        )}

        {/* 处理进度列表 */}
        <div className="progress-section">
          <h3>文案处理进度</h3>
          <div className="progress-items">
            {sessionData.selectedCopywriting.map((item, index) => {
              const videoCompleted = completedVideos.find(v => v.index === index + 1)
              return (
                <div key={item.record_id} className="progress-item">
                  <div className="progress-item-header">
                    <span className="progress-item-number">#{index + 1}</span>
                    <span className="progress-item-text">
                      {item.fields['原文案']?.substring(0, 50)}...
                    </span>
                    <span className={`progress-item-status ${videoCompleted ? 'completed' : ''}`}>
                      {videoCompleted ? '✅ 已完成' : '⏳ 处理中...'}
                    </span>
                  </div>
                  <div className="progress-bar-wrapper">
                    <div
                      className="progress-bar-fill"
                      style={{ width: videoCompleted ? '100%' : (isProcessing ? '50%' : '0%') }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* 处理日志 */}
        <div className="logs-section">
          <div className="logs-header">
            <h3>处理日志</h3>
            <button className="btn-clear-logs" onClick={() => setLogs([])}>
              清空日志
            </button>
          </div>
          <div className="logs-container">
            {logs.map((log, index) => (
              <div key={index} className={`log-item log-${log.level}`}>
                <span className="log-time">{log.time}</span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        {/* 处理完成后的视频预览区域 */}
        {allCompleted && (
          <div className={`completion-section ${showResults ? 'expanded' : ''}`}>
            <div className="completion-header" onClick={toggleResults}>
              <h3>🎉 处理完成</h3>
              <span className="completion-toggle">
                {showResults ? '▲' : '▼'}
              </span>
            </div>

            {showResults && (
              <div className="completion-content">
                <div className="result-notice">
                  <p>✓ 视频已生成{completedVideos.some(v => !v.is_local) ? '并上传到云端' : ''}</p>
                  {completedVideos.some(v => v.is_local) && (
                    <p className="local-notice">ℹ️ 部分视频为本地文件，可通过视频链接访问</p>
                  )}
                </div>

                <div className="video-previews">
                  {completedVideos.map((video, index) => (
                    <div key={index} className="video-preview-card">
                      <div className="video-preview-header">
                        <span className="video-number">视频 #{video.index}</span>
                        <span className="video-title">{video.title || '未命名视频'}</span>
                        {video.is_local && (
                          <span className="video-badge local">本地</span>
                        )}
                      </div>

                      <div className="video-preview-container">
                        {video.preview_url ? (
                          <video
                            className="video-player"
                            controls
                            preload="metadata"
                            poster="/video-placeholder.png"
                          >
                            <source src={`http://localhost:8001${video.preview_url}`} type="video/mp4" />
                            您的浏览器不支持视频播放
                          </video>
                        ) : (
                          <div className="video-placeholder">
                            <div className="placeholder-icon">🎬</div>
                            <p>视频已生成</p>
                            <p className="placeholder-hint">暂无预览</p>
                          </div>
                        )}
                      </div>

                      <div className="video-preview-actions">
                        <a
                          href={video.is_local ? `http://localhost:8001${video.preview_url}` : video.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-action btn-view"
                        >
                          <span className="btn-icon">🔗</span>
                          {video.is_local ? '打开视频' : '打开视频链接'}
                        </a>
                        {video.url && !video.is_local && (
                          <button
                            className="btn-action btn-download"
                            onClick={() => {
                              const link = document.createElement('a')
                              link.href = video.url
                              link.download = `video_${video.index}.mp4`
                              link.click()
                            }}
                          >
                            <span className="btn-icon">⬇️</span>
                            下载视频
                          </button>
                        )}
                        {video.is_local && (
                          <button
                            className="btn-action btn-info"
                            onClick={() => openVideoFolder(video)}
                          >
                            <span className="btn-icon">📁</span>
                            文件路径
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="completion-actions">
                  <button className="btn-primary" onClick={handleRestart}>
                    🔄 处理新文案
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={() => window.location.reload()}
                  >
                    🏠 返回首页
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ProcessingPage
