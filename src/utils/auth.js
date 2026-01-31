/**
 * 用户认证工具
 */

/**
 * 获取当前用户信息
 * @returns {Promise<Object|null>} 用户信息或null
 */
export async function getCurrentUser() {
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    })
    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
  return null
}

/**
 * 登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise<boolean>} 是否登录成功
 */
export async function login(username, password) {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    })
    return response.ok
  } catch (error) {
    console.error('登录失败:', error)
    return false
  }
}

/**
 * 登出
 * @returns {Promise<boolean>} 是否登出成功
 */
export async function logout() {
  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })
    return response.ok
  } catch (error) {
    console.error('登出失败:', error)
    return false
  }
}

/**
 * 检查是否已登录
 * @returns {Promise<boolean>} 是否已登录
 */
export async function isAuthenticated() {
  const user = await getCurrentUser()
  return user !== null
}
