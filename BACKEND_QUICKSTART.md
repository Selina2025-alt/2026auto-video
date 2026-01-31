# 快速开始指南

欢迎使用批量自动剪辑智能体！本指南将帮助您快速上手。

## 前置要求

### 必需软件

1. **Python 3.8+**
   - 下载地址: https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **Node.js 16+**
   - 下载地址: https://nodejs.org/
   - 选择 LTS 版本

3. **FFmpeg**
   - 下载地址: https://ffmpeg.org/download.html
   - 或使用包管理器安装: `choco install ffmpeg` (Windows)

### 必需的 Python 包

```bash
pip install fastapi uvicorn
pip install edge-tts
pip install python-multipart
```

### 必需的 Node 包

```bash
npm install
```

## 配置步骤

### 1. 飞书应用配置

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 开通权限：
   - `bitable:app` - 读取和写入多维表格
   - `bitable:app:readonly` - 读取多维表格

### 2. 飞书表格配置

1. 创建多维表格，包含以下字段：
   - `原文案` - 文本类型
   - `视频链接` - URL 类型
   - `状态` - 单选类型

2. 从表格 URL 中获取：
   - Base Token: `https://example.feishu.cn/base/{baseToken}/...`
   - Table ID: 点击表格后在 URL 中找到

### 3. 素材配置（可选）

配置本地素材文件夹路径，系统会优先使用本地素材。

### 4. OSS 配置（可选）

如果需要上传视频到阿里云OSS，请填写：
- Access Key ID
- Access Key Secret
- Bucket 名称
- Endpoint

## 启动服务

### 方式一：使用批处理文件（推荐）

双击运行：
- `启动后端.bat`
- `启动前端.bat`

### 方式二：手动启动

**后端：**
```bash
cd backend
python start.py
```

**前端：**
```bash
npm run dev
```

## 使用流程

1. 访问 http://localhost:5173
2. 首次使用需要配置系统设置
3. 连接飞书表格
4. 选择要处理的文案
5. 点击「开始处理」
6. 等待处理完成
7. 在飞书表格中查看生成的视频链接

## 常见问题

### Q: FFmpeg 未找到？
A: 确保 FFmpeg 已安装并添加到系统 PATH。

### Q: 飞书连接失败？
A: 检查 App ID、App Secret 是否正确，网络是否正常。

### Q: 视频生成失败？
A: 检查素材路径、OSS配置是否正确。

### Q: 配音没有声音？
A: 确保 edge-tts 已安装: `pip install edge-tts`

## 技术支持

遇到问题请查看：
- [完整文档](README.md)
- [问题解决方案](疑难问题解决方案.md)
