/**
 * 本地存储工具
 */

const STORAGE_KEYS = {
  USER_SETTINGS: 'auto_video_settings',
  SESSION_DATA: 'auto_video_session',
  HAS_CONFIGURED: 'auto_video_configured'
}

/**
 * 获取用户设置
 * @returns {Object} 用户设置
 */
export function getUserSettings() {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.USER_SETTINGS)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('获取用户设置失败:', error)
    return null
  }
}

/**
 * 保存用户设置
 * @param {Object} settings 用户设置
 */
export function saveUserSettings(settings) {
  try {
    localStorage.setItem(STORAGE_KEYS.USER_SETTINGS, JSON.stringify(settings))
  } catch (error) {
    console.error('保存用户设置失败:', error)
  }
}

/**
 * 获取会话数据
 * @returns {Object} 会话数据
 */
export function getSessionData() {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.SESSION_DATA)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('获取会话数据失败:', error)
    return null
  }
}

/**
 * 保存会话数据
 * @param {Object} sessionData 会话数据
 */
export function saveSessionData(sessionData) {
  try {
    localStorage.setItem(STORAGE_KEYS.SESSION_DATA, JSON.stringify(sessionData))
  } catch (error) {
    console.error('保存会话数据失败:', error)
  }
}

/**
 * 清除会话数据
 */
export function clearSessionData() {
  try {
    localStorage.removeItem(STORAGE_KEYS.SESSION_DATA)
  } catch (error) {
    console.error('清除会话数据失败:', error)
  }
}

/**
 * 检查是否已配置
 * @returns {boolean} 是否已配置
 */
export function hasConfigured() {
  try {
    return localStorage.getItem(STORAGE_KEYS.HAS_CONFIGURED) === 'true'
  } catch (error) {
    return false
  }
}

/**
 * 设置已配置标记
 * @param {boolean} configured 是否已配置
 */
export function setConfigured(configured) {
  try {
    localStorage.setItem(STORAGE_KEYS.HAS_CONFIGURED, String(configured))
  } catch (error) {
    console.error('设置配置标记失败:', error)
  }
}

/**
 * 清除所有存储数据
 */
export function clearAll() {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key)
    })
  } catch (error) {
    console.error('清除存储数据失败:', error)
  }
}
