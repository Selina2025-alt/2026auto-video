/**
 * 配置记忆工具
 * 用于本地存储和检索用户配置
 */

const CONFIG_PREFIX = 'auto_video_config_'
const REMEMBER_KEY = 'auto_video_remember_enabled'

/**
 * 获取配置
 * @param {string} key - 配置键 (feishu, materials, output)
 * @returns {Object|null} 配置对象
 */
export function getConfig(key) {
  try {
    const fullKey = CONFIG_PREFIX + key
    const data = localStorage.getItem(fullKey)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('获取配置失败:', error)
    return null
  }
}

/**
 * 保存配置
 * @param {string} key - 配置键
 * @param {Object} config - 配置对象
 */
export function saveConfig(key, config) {
  try {
    const fullKey = CONFIG_PREFIX + key
    localStorage.setItem(fullKey, JSON.stringify(config))
  } catch (error) {
    console.error('保存配置失败:', error)
  }
}

/**
 * 检查是否应该询问用户是否记住配置
 * @returns {boolean} 是否应该询问
 */
export function shouldAskRemember() {
  try {
    // 如果用户已经做出选择，就不再询问
    const hasChosen = localStorage.getItem(REMEMBER_KEY)
    return hasChosen === null
  } catch (error) {
    return false
  }
}

/**
 * 确认是否记住配置
 * @param {boolean} confirmed - 用户是否确认记住
 */
export function confirmRemember(confirmed) {
  try {
    localStorage.setItem(REMEMBER_KEY, confirmed ? 'true' : 'false')
  } catch (error) {
    console.error('保存记忆设置失败:', error)
  }
}

/**
 * 检查是否启用了配置记忆功能
 * @returns {boolean} 是否已启用记忆
 */
export function isRememberEnabled() {
  try {
    return localStorage.getItem(REMEMBER_KEY) === 'true'
  } catch (error) {
    return false
  }
}

/**
 * 清除所有记住的配置
 */
export function clearAllConfigs() {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(CONFIG_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
    localStorage.removeItem(REMEMBER_KEY)
  } catch (error) {
    console.error('清除配置失败:', error)
  }
}
