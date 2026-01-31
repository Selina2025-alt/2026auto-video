# 后端服务说明

## 目录结构

```
backend/
├── main.py              # FastAPI 主应用
├── start.py             # 启动脚本
├── config.py            # 配置模块
├── requirements.txt     # Python 依赖
├── config.example.yaml  # 配置示例
│
├── auth/                # 用户认证模块
│   ├── db.py           # 用户数据库
│   └── models.py       # 用户模型
│
├── feishu/             # 飞书集成模块
│   ├── client.py       # 飞书客户端
│   └── table_handler.py # 表格处理器
│
├── text_processor/     # 文本处理模块
│   └── processor.py    # 文案处理器
│
├── audio/              # 音频生成模块
│   └── tts_generator.py # TTS生成器
│
├── material_matcher/   # 素材匹配模块
│   ├── matcher.py            # 主匹配器
│   ├── firecrawl_client.py  # 网页抓取
│   └── ai_video_generator.py # AI视频生成
│
├── video_editor/       # 视频编辑模块
│   └── editor.py       # 视频编辑器
│
├── storage/            # 存储模块
│   └── oss_uploader.py # OSS上传器
│
└── processor/          # 处理编排模块
    └── video_processor.py # 视频处理器
```

## 核心模块说明

### 1. 认证模块 (auth/)

提供简单的用户认证功能：
- 用户登录/登出
- 会话管理
- 用户数据存储（JSON文件）

### 2. 飞书模块 (feishu/)

飞书开放平台集成：
- 读取多维表格数据
- 回写处理结果
- 更新记录状态

### 3. 文本处理模块 (text_processor/)

文案预处理：
- 清理表情符号和口语化表达
- 智能场景拆分
- 关键词提取

### 4. 音频生成模块 (audio/)

TTS语音合成：
- 使用 Edge TTS
- 支持多种语音
- 批量生成

### 5. 素材匹配模块 (material_matcher/)

视频素材匹配：
- 本地素材搜索
- Pexels API 集成
- 预留更多素材库接口

### 6. 视频编辑模块 (video_editor/)

视频处理：
- 基于 FFmpeg
- 视频合成和拼接
- 背景音乐添加

### 7. 存储模块 (storage/)

云存储集成：
- 阿里云 OSS 上传
- 本地文件预览

### 8. 处理编排模块 (processor/)

完整流程编排：
- 整合所有模块
- 14步人性化流程
- 进度回调机制

## API 端点

### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户

### 飞书相关
- `POST /api/feishu/tables` - 获取表格列表
- `POST /api/feishu/tables/{table_id}/records` - 获取记录
- `POST /api/feishu/test` - 测试连接

### 处理相关
- `POST /api/process/start` - 开始处理
- `GET /api/process/status/{task_id}` - 获取状态

### 设置相关
- `GET /api/settings/get` - 获取配置
- `POST /api/settings/save` - 保存配置

### WebSocket
- `WS /ws` - 实时进度推送

## 依赖安装

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
python start.py
```

或使用批处理文件：
```bash
start_backend.bat
```

## 环境变量

可通过环境变量覆盖配置：
- `PORT` - 服务端口（默认 8001）
- `DEBUG` - 调试模式
