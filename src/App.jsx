import React, { useState, useEffect } from 'react'
import WelcomePage from './components/WelcomePage.jsx'
import LoginPage from './components/LoginPage.jsx'
import StepFeishu from './components/steps/StepFeishu.jsx'
import StepSelectCopy from './components/steps/StepSelectCopy.jsx'
import StepMaterials from './components/steps/StepMaterials.jsx'
import StepOutput from './components/steps/StepOutput.jsx'
import ProcessingPage from './components/ProcessingPage.jsx'
import Settings from './components/Settings.jsx'
import './App.css'

function App() {
  const [currentStep, setCurrentStep] = useState('welcome') // welcome, login, feishu, select, materials, output, processing
  const [user, setUser] = useState(null)
  const [showSettings, setShowSettings] = useState(false)
  const [sessiondata, setSessiondata] = useState({
    feishu: null,
    copywritingList: [],
    selectedCopywriting: [],
    materialsConfig: null,
    outputConfig: null
  })

  useEffect(() => {
    // 检查是否有已登录的用户
    checkUserSession()
  }, [])

  const checkUserSession = async () => {
    try {
      const response = await fetch('/api/auth/session', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.user) {
          setUser(data.user)
          setCurrentStep('feishu')
        }
      }
    } catch (error) {
      console.log('未登录或会话已过期')
    }
  }

  const handleStartClick = () => {
    setCurrentStep('login')
  }

  const handleLoginSuccess = (userdata) => {
    setUser(userdata)
    setCurrentStep('feishu')
  }

  const handleFeishuComplete = (feishudata) => {
    setSessiondata(prev => ({ ...prev, feishu: feishudata }))
    setCurrentStep('select')
  }

  const handleSelectComplete = (selectedItems) => {
    setSessiondata(prev => ({ ...prev, selectedCopywriting: selectedItems }))
    setCurrentStep('materials')
  }

  const handleMaterialsComplete = (materialsConfig) => {
    setSessiondata(prev => ({ ...prev, materialsConfig }))
    setCurrentStep('output')
  }

  const handleOutputComplete = (outputConfig) => {
    setSessiondata(prev => ({ ...prev, outputConfig }))
    setCurrentStep('processing')
  }

  const handleBack = () => {
    const steps = ['welcome', 'login', 'feishu', 'select', 'materials', 'output', 'processing']
    const currentIndex = steps.indexOf(currentStep)
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1])
    }
  }

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      })
      setUser(null)
      setCurrentStep('welcome')
      setSessiondata({
        feishu: null,
        copywritingList: [],
        selectedCopywriting: [],
        materialsConfig: null,
        outputConfig: null
      })
    } catch (error) {
      console.error('退出登录失败', error)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎬 批量自动剪辑智能体</h1>
          {user && (
            <div className="user-info">
              <button className="btn-settings" onClick={() => setShowSettings(true)}>
                ⚙️ 设置
              </button>
              <span>👤 {user.username || user.email}</span>
              <button className="btn-logout" onClick={handleLogout}>退出</button>
            </div>
          )}
        </div>
      </header>

      <div className="app-container">
        {currentStep === 'welcome' && (
          <WelcomePage onStart={handleStartClick} />
        )}
        
        {currentStep === 'login' && (
          <LoginPage onLoginSuccess={handleLoginSuccess} />
        )}
        
        {currentStep === 'feishu' && (
          <StepFeishu 
            user={user}
            onComplete={handleFeishuComplete}
            onBack={handleBack}
          />
        )}
        
        {currentStep === 'select' && (
          <StepSelectCopy 
            copywritingList={sessiondata.feishu?.copywritingList || []}
            onComplete={handleSelectComplete}
            onBack={handleBack}
          />
        )}
        
        {currentStep === 'materials' && (
          <StepMaterials 
            user={user}
            onComplete={handleMaterialsComplete}
            onBack={handleBack}
          />
        )}
        
        {currentStep === 'output' && (
          <StepOutput 
            user={user}
            onComplete={handleOutputComplete}
            onBack={handleBack}
          />
        )}
        
        {currentStep === 'processing' && (
          <ProcessingPage
            sessionData={sessiondata}
            user={user}
          />
        )}
      </div>

      <footer className="app-footer">
        <p>Auto Video Agent v2.0 | 智能引导式处理流程</p>
      </footer>

      {showSettings && (
        <Settings onClose={() => setShowSettings(false)} />
      )}
    </div>
  )
}

export default App
