import React, { useState } from 'react'
import './LoginPage.css'

function LoginPage({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // 测试环境：允许空白登录
    const isTestMode = false // 测试模式开关
    
    if (isTestMode) {
      // 测试模式直接跳过验证，模拟登录成功
      setTimeout(() => {
        onLoginSuccess({
          user_id: 'test_user',
          email: 'test@example.com',
          username: '测试用户'
        })
        setLoading(false)
      }, 500)
      return
    }

    // 表单验证（生产环境）
    if (!formData.email || !formData.password) {
      setError('请填写所有必填项')
      setLoading(false)
      return
    }

    if (!isLogin) {
      if (!formData.username) {
        setError('请输入用户名')
        setLoading(false)
        return
      }
      if (formData.password !== formData.confirmPassword) {
        setError('两次输入的密码不一致')
        setLoading(false)
        return
      }
      if (formData.password.length < 6) {
        setError('密码长度至少6位')
        setLoading(false)
        return
      }
    }

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register'
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : { email: formData.email, username: formData.username, password: formData.password }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
        credentials: 'include'
      })

      const data = await response.json()

      if (response.ok) {
        onLoginSuccess(data.user)
      } else {
        setError(data.message || '登录失败，请重试')
      }
    } catch (error) {
      setError('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const toggleMode = () => {
    setIsLogin(!isLogin)
    setError('')
    setFormData({
      email: '',
      username: '',
      password: '',
      confirmPassword: ''
    })
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h2>{isLogin ? '👋 欢迎回来' : '🎉 创建账号'}</h2>
          <p>{isLogin ? '登录以继续使用' : '注册新账号开始使用'}</p>
          <p style={{ fontSize: '0.9rem', opacity: 0.8, marginTop: '0.5rem' }}>
            🧪 测试模式：直接点击登录即可
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <div className="form-group">
            <label>邮箱地址</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="your@email.com（测试模式可留空）"
              />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>用户名</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="设置用户名"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>密码</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder={isLogin ? "输入密码（测试模式可留空）" : "设置密码（至少6位）"}
              />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>确认密码</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="再次输入密码"
                required
              />
            </div>
          )}

          <button 
            type="submit" 
            className="btn-submit"
            disabled={loading}
          >
            {loading ? '处理中...' : (isLogin ? '登录' : '注册')}
          </button>
        </form>

        <div className="login-footer">
          <p>
            {isLogin ? '还没有账号？' : '已有账号？'}
            <button className="btn-toggle" onClick={toggleMode}>
              {isLogin ? '立即注册' : '立即登录'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
