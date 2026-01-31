/**
 * API 请求工具
 */

/**
 * 封装的 fetch 请求
 * @param {string} url 请求URL
 * @param {Object} options 请求选项
 * @returns {Promise<Response>} 响应
 */
export async function fetchAPI(url, options = {}) {
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }

  return fetch(url, { ...defaultOptions, ...options })
}

/**
 * GET 请求
 * @param {string} url 请求URL
 * @param {Object} params 查询参数
 * @returns {Promise<Object>} 响应数据
 */
export async function get(url, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const fullUrl = queryString ? `${url}?${queryString}` : url

  const response = await fetchAPI(fullUrl)
  if (response.ok) {
    return await response.json()
  }
  throw new Error(`GET 请求失败: ${response.status}`)
}

/**
 * POST 请求
 * @param {string} url 请求URL
 * @param {Object} data 请求体数据
 * @returns {Promise<Object>} 响应数据
 */
export async function post(url, data = {}) {
  const response = await fetchAPI(url, {
    method: 'POST',
    body: JSON.stringify(data)
  })
  if (response.ok) {
    return await response.json()
  }
  throw new Error(`POST 请求失败: ${response.status}`)
}

/**
 * PUT 请求
 * @param {string} url 请求URL
 * @param {Object} data 请求体数据
 * @returns {Promise<Object>} 响应数据
 */
export async function put(url, data = {}) {
  const response = await fetchAPI(url, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
  if (response.ok) {
    return await response.json()
  }
  throw new Error(`PUT 请求失败: ${response.status}`)
}

/**
 * DELETE 请求
 * @param {string} url 请求URL
 * @returns {Promise<Object>} 响应数据
 */
export async function del(url) {
  const response = await fetchAPI(url, {
    method: 'DELETE'
  })
  if (response.ok) {
    return await response.json()
  }
  throw new Error(`DELETE 请求失败: ${response.status}`)
}

/**
 * 上传文件
 * @param {string} url 上传URL
 * @param {FormData} formData 表单数据
 * @returns {Promise<Object>} 响应数据
 */
export async function upload(url, formData) {
  const response = await fetchAPI(url, {
    method: 'POST',
    headers: {}, // 让浏览器自动设置 Content-Type
    body: formData
  })
  if (response.ok) {
    return await response.json()
  }
  throw new Error(`上传失败: ${response.status}`)
}
