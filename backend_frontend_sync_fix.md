# 前后端同步修复说明

## 问题描述

在开发过程中发现前后端数据格式不一致的问题，导致：
- WebSocket 消息格式混乱
- 视频完成消息字段不匹配
- 配置字段命名不一致

## 修复方案

### 1. WebSocket 消息格式统一

**视频完成消息格式**:
```json
{
  "type": "video_completed",
  "video": {
    "url": "视频URL（云端或本地file://）",
    "preview_url": "预览URL（/output/路径）",
    "is_local": "是否为本地文件",
    "title": "视频标题",
    "record_id": "记录ID",
    "index": "索引"
  }
}
```

**步骤消息格式**:
```json
{
  "type": "step",
  "step_name": "步骤名称",
  "message": "步骤描述",
  "details": {
    "step_number": 当前步骤号,
    "total_steps": 总步骤数,
    "progress": 进度百分比 (0-1)
  }
}
```

### 2. 配置字段兼容性

后端同时支持新旧两种配置格式：

**旧格式** (前端使用):
```python
'output': {
    'ossAccessKeyId': 'xxx',
    'ossAccessKeySecret': 'xxx',
    'ossBucketName': 'xxx',
    'ossEndpoint': 'xxx'
}
```

**新格式** (后端内部):
```python
'output': {
    'access_key_id': 'xxx',
    'access_key_secret': 'xxx',
    'bucket_name': 'xxx',
    'endpoint': 'xxx'
}
```

### 3. 视频预览功能

**本地视频预览**:
- 后端添加静态文件服务: `app.mount("/output", ...)`
- 生成预览URL: `/output/{user_id}/videos/{filename}`
- 前端使用: `http://localhost:8001{preview_url}`

**云端视频预览**:
- 直接使用云端 URL
- 支持下载功能

### 4. 错误处理改进

- WebSocket 断线自动重连
- 降级到轮询模式
- 友好的错误提示

## 测试验证

1. 启动后端服务
2. 启动前端服务
3. 测试完整处理流程
4. 验证视频预览功能
5. 检查 WebSocket 消息

## 相关文件

- `backend/main.py` - WebSocket 消息处理
- `backend/processor/video_processor.py` - 配置兼容
- `src/components/ProcessingPage.jsx` - 前端处理
