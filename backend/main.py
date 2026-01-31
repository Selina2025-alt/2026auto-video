"""
批量自动剪辑智能体 - 后端主入口
FastAPI应用程序
"""
import sys
import io

# 设置标准输出为UTF-8编码，避免Windows GBK编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
import os

from auth.db import user_db
from auth.models import User

app = FastAPI(title="Auto Video Agent API", version="2.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载输出目录作为静态文件服务（用于本地视频预览）
output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
if os.path.exists(output_dir):
    app.mount("/output", StaticFiles(directory=output_dir), name="output")

# Session管理（简化版，生产环境使用Redis等）
sessions: Dict[str, str] = {}  # session_id -> user_id

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Pydantic模型
class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class FeishuConfigRequest(BaseModel):
    appId: str
    appSecret: str
    baseToken: str
    tableId: str

# 辅助函数
def get_session_id(request: Request) -> Optional[str]:
    """从cookie获取session ID"""
    return request.cookies.get('session_id')

def get_current_user(request: Request) -> Optional[User]:
    """获取当前登录用户"""
    session_id = get_session_id(request)
    if not session_id or session_id not in sessions:
        return None
    user_id = sessions[session_id]
    return user_db.get_user_by_id(user_id)

def create_session(user_id: str) -> str:
    """创建session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = user_id
    return session_id

# API路由
@app.get("/")
async def root():
    return {"message": "Auto Video Agent API v2.0 is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# 认证API
@app.post("/api/auth/register")
async def register(req: RegisterRequest, response: Response):
    """用户注册"""
    try:
        user = user_db.create_user(req.email, req.username, req.password)
        session_id = create_session(user.user_id)
        response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax")
        return {"success": True, "user": user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="注册失败")

@app.post("/api/auth/login")
async def login(req: LoginRequest, response: Response):
    """用户登录"""
    user = user_db.get_user_by_email(req.email)
    if not user or not User.verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    user_db.update_last_login(user.user_id)
    session_id = create_session(user.user_id)
    response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax")
    return {"success": True, "user": user.to_dict()}

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """用户登出"""
    session_id = get_session_id(request)
    if session_id and session_id in sessions:
        del sessions[session_id]
    response.delete_cookie("session_id")
    return {"success": True}

@app.get("/api/auth/session")
async def get_session(request: Request):
    """获取当前session"""
    user = get_current_user(request)
    if user:
        return {"user": user.to_dict()}
    return {"user": None}

# 用户配置API
@app.get("/api/user/config/{config_type}")
async def get_config(config_type: str, request: Request):
    """获取用户配置"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    config = user_db.get_user_config(user.user_id, config_type)
    return {"config": config}

@app.post("/api/user/config/{config_type}")
async def save_config(config_type: str, config_data: Dict[str, Any], request: Request):
    """保存用户配置"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    user_db.update_user_config(user.user_id, config_type, config_data)
    return {"success": True}

# 飞书API
@app.post("/api/feishu/test-connection")
async def test_feishu_connection(config: FeishuConfigRequest, request: Request):
    """测试飞书连接并读取表格"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    try:
        print(f"\n=== 飞书连接测试 ===")
        print(f"App ID: {config.appId}")
        print(f"Base Token: {config.baseToken}")
        print(f"Table ID: {config.tableId}")
        
        from feishu.client import FeishuClient
        from feishu.table_handler import TableHandler
        
        # 创建客户端
        client = FeishuClient(config.appId, config.appSecret)
        print("[OK] 客户端创建成功")
        
        # 获取token
        try:
            token = client.get_tenant_access_token()
            print(f"[OK] Token获取成功: {token[:20]}...")
        except Exception as token_error:
            print(f"[ERROR] Token获取失败: {str(token_error)}")
            raise Exception(f"获取访问令牌失败，请检查App ID和App Secret是否正确: {str(token_error)}")
        
        # 创建表格处理器
        handler = TableHandler(client, config.baseToken, config.tableId)
        print("[OK] 表格处理器创建成功")
        
        # 读取文案列表
        try:
            copywriting_list = handler.get_all_copywriting()
            print(f"[OK] 读取到 {len(copywriting_list)} 条记录")
        except Exception as read_error:
            print(f"[ERROR] 读取记录失败: {str(read_error)}")
            raise Exception(f"读取表格数据失败，请检查Base Token和Table ID是否正确，以及应用权限是否配置: {str(read_error)}")
        
        return {
            "success": True,
            "copywritingList": copywriting_list,
            "count": len(copywriting_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 连接失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"连接失败: {str(e)}")

# 处理任务存储
processing_tasks: Dict[str, Dict[str, Any]] = {}

# 处理API
@app.post("/api/process/start")
async def start_processing(session_data: Dict[str, Any], request: Request):
    """开始处理视频"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    # 添加调试日志
    print(f"\n=== 开始处理请求 ===")
    print(f"收到的session_data keys: {list(session_data.keys())}")
    print(f"selectedCopywriting数量: {len(session_data.get('selectedCopywriting', []))}")
    
    try:
        from processor.video_processor import VideoProcessor
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        print(f"生成任务ID: {task_id}")
        
        # 准备配置 - 注意前端传的字段名，需要转换
        materials_raw = session_data.get('materialsConfig', session_data.get('materials', {}))
        output_raw = session_data.get('outputConfig', session_data.get('output', {}))
        
        # 转换前端字段名到后端字段名
        materials_config = {
            'local_path': materials_raw.get('localPath', materials_raw.get('local_path', './local_materials')),
            'use_local_materials': materials_raw.get('useLocalMaterials', True),
            'use_web_search': materials_raw.get('useWebSearch', True),
            'pexels_api_key': materials_raw.get('materialApis', {}).get('pexels', ''),
            'freepik_api_key': materials_raw.get('materialApis', {}).get('freepik', ''),
            'coverr_api_key': materials_raw.get('materialApis', {}).get('coverr', ''),
            'firecrawl_api_key': materials_raw.get('materialApis', {}).get('firecrawl', ''),
            'ai_mode': materials_raw.get('aiVideoGeneration', {}).get('mode', 'skip'),
        }
        
        output_config = {
            'oss_access_key_id': output_raw.get('ossAccessKeyId', output_raw.get('access_key_id', '')),
            'oss_access_key_secret': output_raw.get('ossAccessKeySecret', output_raw.get('access_key_secret', '')),
            'oss_bucket_name': output_raw.get('ossBucketName', output_raw.get('bucket_name', '')),
            'oss_endpoint': output_raw.get('ossEndpoint', output_raw.get('endpoint', '')),
            'access_key_id': output_raw.get('ossAccessKeyId', output_raw.get('access_key_id', '')),
            'access_key_secret': output_raw.get('ossAccessKeySecret', output_raw.get('access_key_secret', '')),
            'bucket_name': output_raw.get('ossBucketName', output_raw.get('bucket_name', '')),
            'endpoint': output_raw.get('ossEndpoint', output_raw.get('endpoint', '')),
        }
        
        config = {
            'user_id': user.user_id,
            'feishu': session_data.get('feishu', {}),
            'materials': materials_config,
            'output': output_config
        }
        print(f"配置keys: feishu={bool(config['feishu'])}, materials={bool(config['materials'])}, output={bool(config['output'])}")
        print(f"素材配置: local_path={materials_config.get('local_path')}")
        print(f"output配置内容: {config['output']}")
        
        # 获取要处理的文案列表
        selected_copywriting = session_data.get('selectedCopywriting', [])
        print(f"选中的文案: {len(selected_copywriting)} 条")
        
        if not selected_copywriting:
            print("[ERROR] 未选择文案!")
            raise HTTPException(status_code=400, detail="未选择文案")
        
        # 创建处理器
        processor = VideoProcessor(config)
        
        # 记录任务
        processing_tasks[task_id] = {
            'status': 'processing',
            'total': len(selected_copywriting),
            'completed': 0,
            'results': []
        }
        
        # 在后台异步处理
        asyncio.create_task(
            process_videos_background(
                task_id,
                processor,
                selected_copywriting
            )
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "处理任务已启动"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动处理失败: {str(e)}")

async def process_videos_background(
    task_id: str,
    processor,
    copywriting_list: List[Dict[str, Any]]
):
    """后台处理视频"""
    print(f"\n=== 后台任务开始 ===")
    print(f"任务ID: {task_id}")
    print(f"文案数量: {len(copywriting_list)}")
    if copywriting_list:
        print(f"第一条文案keys: {list(copywriting_list[0].keys()) if copywriting_list[0] else 'empty'}")
    
    try:
        async def progress_callback(msg_type, message, progress_value, extra):
            """
            处理进度回调
            msg_type: 'start', 'step_start', 'step_success', 'step_detail', 'completed', 'completed_detail', 'error'
            message: 显示给用户的消息
            progress_value: 进度值 (0-1)
            extra: 额外信息 (如step_number, total_steps等)
            """
            # 构建WebSocket消息
            ws_message = {
                'task_id': task_id,
                'message': message
            }
            
            # 根据消息类型设置type和其他字段
            if msg_type == 'start':
                ws_message['type'] = 'log'
            elif msg_type == 'step_start':
                ws_message['type'] = 'step'
                if extra:
                    ws_message['step_name'] = extra.get('step_name', '')
                    ws_message['details'] = {
                        'progress': round((extra.get('step_number', 0) / extra.get('total_steps', 14)) * 100)
                    }
            elif msg_type == 'step_success' or msg_type == 'step_detail':
                ws_message['type'] = 'log'
            elif msg_type == 'completed' or msg_type == 'completed_detail':
                ws_message['type'] = 'log'
                if msg_type == 'completed':
                    ws_message['completed'] = True
            elif msg_type == 'error':
                ws_message['type'] = 'error'
            else:
                ws_message['type'] = 'log'
            
            # 广播消息
            await manager.broadcast(json.dumps(ws_message))
        
        # 批量处理（但现在我们一次处理一条，以便展示详细步骤）
        for idx, copywriting_item in enumerate(copywriting_list, 1):
            print(f"\n--- 处理第 {idx} 条文案 ---")
            print(f"copywriting_item: {copywriting_item}")
            
            # 发送批次进度
            await manager.broadcast(json.dumps({
                'type': 'log',
                'task_id': task_id,
                'message': f'开始处理第 {idx}/{len(copywriting_list)} 条文案...'
            }))
            
            # 提取文案文本
            text = ''
            if 'fields' in copywriting_item:
                text = copywriting_item['fields'].get('原文案', '')
            elif 'text' in copywriting_item:
                text = copywriting_item.get('text', '')
            
            # 准备处理数据
            process_item = {
                'record_id': copywriting_item.get('record_id', copywriting_item.get('id', f'temp_{idx}')),
                'text': text
            }
            print(f"处理数据: record_id={process_item['record_id']}, text长度={len(process_item['text'])}")
            
            try:
                # 处理单条
                result = await processor.process_copywriting(
                    process_item,
                    progress_callback=progress_callback
                )
                print(f"处理结果: {result}")
            except Exception as process_error:
                print(f"[ERROR] 处理文案出错: {process_error}")
                import traceback
                traceback.print_exc()
                result = {'success': False, 'error': str(process_error)}
            
            # 更新任务进度
            processing_tasks[task_id]['completed'] = idx
            processing_tasks[task_id]['results'].append(result)
            
            # #region agent log - 假设C1: 检查处理结果
            log_path = r'd:\koubinyue\Cursor\20260128auto-video\.cursor\debug.log'
            import time as _time
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"hypothesisId":"C1","location":"main.py:process_result","message":"视频处理结果","data":{"success":result.get('success'),"video_url":result.get('video_url',''),"error":result.get('error','')},"timestamp":_time.time()}) + '\n')
            # #endregion
            
            # 如果成功，发送视频完成消息
            if result.get('success'):
                # 解析视频URL，如果是本地路径则生成预览URL
                video_url = result.get('video_url', '')
                preview_url = video_url

                if video_url and video_url.startswith('file://'):
                    # 本地文件，生成预览URL
                    local_path = video_url.replace('file://', '')
                    filename = os.path.basename(local_path)
                    preview_url = f"/output/{user.user_id}/videos/{filename}"

                video_info = {
                    'url': video_url,
                    'preview_url': preview_url,
                    'is_local': video_url.startswith('file://') if video_url else False,
                    'title': copywriting_item.get('text', '')[:50] + '...' if len(copywriting_item.get('text', '')) > 50 else copywriting_item.get('text', ''),
                    'record_id': copywriting_item.get('record_id', ''),
                    'index': idx
                }
                
                # #region agent log - 假设C1: 发送video_completed消息
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"hypothesisId":"C1","location":"main.py:video_completed_msg","message":"发送video_completed消息","data":{"video_info":video_info},"timestamp":_time.time()}) + '\n')
                # #endregion
                
                await manager.broadcast(json.dumps({
                    'type': 'video_completed',
                    'task_id': task_id,
                    'video': video_info
                }))
        
        # 更新任务状态
        processing_tasks[task_id]['status'] = 'completed'
        
        # 发送全部完成通知
        await manager.broadcast(json.dumps({
            'type': 'all_completed',
            'task_id': task_id,
            'total': len(copywriting_list)
        }))
    
    except Exception as e:
        processing_tasks[task_id]['status'] = 'failed'
        processing_tasks[task_id]['error'] = str(e)
        
        await manager.broadcast(json.dumps({
            'type': 'error',
            'task_id': task_id,
            'error': str(e)
        }))

@app.get("/api/process/status/{task_id}")
async def get_processing_status(task_id: str, request: Request):
    """获取处理任务状态"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")

    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    return processing_tasks[task_id]

@app.get("/api/video/local/{user_id}/{filename}")
async def get_local_video_info(user_id: str, filename: str, request: Request):
    """获取本地视频信息（用于预览）"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")

    # 构建视频文件路径
    video_path = os.path.join(output_dir, user_id, "videos", filename)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="视频文件不存在")

    return {
        "success": True,
        "local_path": video_path,
        "preview_url": f"/output/{user_id}/videos/{filename}",
        "filename": filename
    }

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点，用于实时推送处理进度"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息（保持连接）
            data = await websocket.receive_text()
            # 可以处理客户端发来的控制消息
            try:
                message = json.loads(data)
                if message.get('type') == 'ping':
                    await websocket.send_text(json.dumps({'type': 'pong'}))
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
