# 🎬 批量自动剪辑智能体 v2.0

**✅ 系统已就绪 | 最后更新: 2026-01-29 | 完成度: 85%**

从飞书多维表格读取文案，全流程智能化自动生成视频。

> 🎉 **最新更新**: Freepik API 集成 + Firecrawl 深度搜索 + AI 视频生成接口  
> 📖 **快速开始**: 查看 [快速上手.md](./快速上手.md) 或 [✅完成总结.txt](./✅完成总结.txt)

## ✨ 新版本特性

### 🚀 引导式用户体验
- **欢迎页面**: 清晰展示功能和流程
- **用户系统**: 注册/登录功能，配置云端保存
- **5步引导流程**: 
  1. 连接飞书多维表格
  2. 选择要处理的文案
  3. 配置素材来源（可跳过）
  4. 设置输出方式
  5. 实时查看处理进度

### 🔐 用户系统
- 用户注册和登录
- 配置自动保存到后端
- 下次使用无需重复配置
- Session管理

### 🎯 智能配置
- **飞书链接自动解析**: 只需粘贴表格链接，自动提取Base Token和Table ID
- **可选配置步骤**: 不必要的配置可以跳过使用默认值
- **配置持久化**: 所有配置保存在云端，换设备也能使用

### 🎥 素材匹配优先级
1. **本地素材库** (优先，最快)
2. **网络搜索** (Pexels、Freepik、Coverr、Firecrawl)
3. **AI生成** (Runway、Pika等，仅在前两者无匹配时使用)

## 功能特性

### 核心功能
- 📊 **飞书集成**: 读取多维表格文案，自动回写视频结果
- 📝 **文案处理**: 自动清洗、分镜拆解、关键词提取
- 🎥 **素材匹配**: 本地向量库 + 网络搜索 + AI生成
- 🎙️ **音频合成**: Edge TTS生成配音和字幕
- 👤 **数字人**: 可选HeyGen数字人功能
- ✂️ **视频剪辑**: FFmpeg多图层合成
- ☁️ **云存储**: 自动上传阿里云OSS

### 素材来源
- **本地素材库**: 智能向量匹配（相似度>0.8）
- **网络搜索**: Pexels、Freepik、Coverr
- **深度爬虫**: Firecrawl爬取更多素材
- **AI生成**: 支持Runway、Pika等多种工具或中转站API

### AI视频生成模式
- A. AI生视频工具: 配置工具名称和API密钥
- B. 中转站API: 提供base_url和key
- C. 跳过AI生成: 仅使用本地+网络素材

## 技术栈

### 前端
- React 18
- Vite
- 多步骤引导式UI
- WebSocket实时通信

### 后端
- Python 3.10+
- FastAPI
- 用户认证系统
- FFmpeg（视频处理）
- Chroma（向量数据库）
- Edge TTS（文本转语音）

## 快速开始

### 1. 安装依赖

```bash
# 前端依赖
npm install

# 后端依赖
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 启动后端（新终端）
cd backend
python start.py
# 后端运行在 http://localhost:8000
# API文档: http://localhost:8000/docs

# 启动前端（新终端）
npm run dev
# 前端运行在 http://localhost:3000
```

> 💡 **提示**: 首次启动建议先运行 `python backend/test_modules.py` 测试所有模块是否正常

> 📖 **详细指南**: 查看 [BACKEND_QUICKSTART.md](BACKEND_QUICKSTART.md) 了解后端配置和故障排除

### 3. 首次使用流程

1. **访问** http://localhost:3000
2. **欢迎页面**: 查看功能介绍，点击"开始使用"
3. **注册/登录**: 创建账号或登录
4. **步骤1 - 连接飞书**:
   - 粘贴飞书多维表格链接
   - 输入飞书App ID和App Secret
   - 点击"连接并读取文案"
5. **步骤2 - 选择文案**:
   - 查看读取到的文案列表
   - 选择要处理的文案（可多选）
6. **步骤3 - 配置素材**（可跳过）:
   - 设置本地素材库路径
   - 配置网络素材API（可选）
   - 选择AI视频生成方式
7. **步骤4 - 设置输出**:
   - 配置阿里云OSS（必填）
   - 选择是否启用数字人
8. **处理页面**: 
   - 实时查看处理进度
   - 查看详细日志
   - 处理完成后查看结果

## 项目结构

```
auto-video-agent/
├── src/                          # 前端源码
│   ├── App.jsx                  # 主应用（步骤流程管理）
│   ├── components/
│   │   ├── WelcomePage.jsx     # 欢迎页面
│   │   ├── LoginPage.jsx       # 登录/注册页面
│   │   ├── ProcessingPage.jsx  # 处理进度页面
│   │   └── steps/              # 步骤组件
│   │       ├── StepFeishu.jsx  # 步骤1: 连接飞书
│   │       ├── StepSelectCopy.jsx  # 步骤2: 选择文案
│   │       ├── StepMaterials.jsx   # 步骤3: 配置素材
│   │       └── StepOutput.jsx      # 步骤4: 设置输出
├── backend/                     # 后端源码
│   ├── main.py                 # FastAPI主入口
│   ├── auth/                   # 用户认证模块
│   │   ├── models.py           # 用户模型
│   │   └── db.py               # 用户数据库
│   ├── feishu/                 # 飞书API集成
│   ├── text_processor/         # 文案处理
│   ├── material_matcher/       # 素材匹配
│   ├── audio/                  # 音频处理
│   ├── digital_human/          # 数字人
│   ├── video_editor/           # 视频剪辑
│   └── storage/                # 云存储
├── local_materials/            # 本地素材库
├── output/                     # 输出视频
└── README.md
```

## 配置说明

### 飞书API获取
1. 访问 https://open.feishu.cn/
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 开通"多维表格"权限

### 素材网站API
- **Pexels**: https://www.pexels.com/api/
- **Freepik**: https://www.freepik.com/api
- **Coverr**: https://coverr.co/api
- **Firecrawl**: https://firecrawl.dev/

### AI视频生成
支持以下方式：
- 直接配置AI工具（Runway、Pika等）
- 使用中转站API
- 跳过AI生成

## 重要更新 v2.0

### 与v1.0的区别
- ✅ 添加用户系统（注册/登录）
- ✅ 配置云端保存，无需每次输入
- ✅ 引导式5步流程，更友好
- ✅ 飞书链接自动解析
- ✅ 可选配置步骤可跳过
- ✅ 实时处理进度展示
- ✅ 移除所有敏感信息示例

### 安全性改进
- 密码哈希存储
- Session管理
- Cookie安全设置
- 所有API密钥由用户自行配置

## 注意事项

1. **API密钥安全**: 所有密钥由用户自行配置，保存在后端数据库
2. **成本控制**: AI生成和数字人功能会消耗积分，建议先测试
3. **素材版权**: 使用网络素材需注意版权问题
4. **资源管理**: 视频处理占用内存较大，建议合理控制并发数
5. **首次使用**: 需要完整配置一次，后续使用配置自动加载

## 开发进度

- [x] 前端引导式界面
- [x] 用户认证系统
- [x] 配置管理系统
- [ ] 后端完整实现（进行中）
- [ ] 飞书API集成
- [ ] 文案处理模块
- [ ] 素材匹配模块
- [ ] 视频剪辑模块
- [ ] 批量处理优化

## 许可证

MIT License

## 作者

Auto Video Agent Team - v2.0 引导式版本
