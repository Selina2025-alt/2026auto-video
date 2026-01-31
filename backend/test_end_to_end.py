"""
端到端测试
测试完整的视频处理流程
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processor.video_processor import VideoProcessor


async def test_end_to_end():
    """端到端测试"""

    print("=" * 60)
    print("端到端测试")
    print("=" * 60)

    # 配置
    config = {
        'user_id': 'test_user',
        'materials': {
            'local_path': './local_materials',
            'pexels_api_key': os.getenv('PEXELS_API_KEY', ''),
        },
        'output': {
            'voice': 'female',
            'ossAccessKeyId': os.getenv('OSS_ACCESS_KEY_ID', ''),
            'ossAccessKeySecret': os.getenv('OSS_ACCESS_KEY_SECRET', ''),
            'ossBucketName': os.getenv('OSS_BUCKET_NAME', ''),
            'ossEndpoint': os.getenv('OSS_ENDPOINT', ''),
        },
        'feishu': {
            'appId': os.getenv('FEISHU_APP_ID', ''),
            'appSecret': os.getenv('FEISHU_APP_SECRET', ''),
            'baseToken': os.getenv('FEISHU_BASE_TOKEN', ''),
            'tableId': os.getenv('FEISHU_TABLE_ID', ''),
        }
    }

    # 创建处理器
    processor = VideoProcessor(config)

    # 测试文案
    test_copywriting = {
        'record_id': 'test_001',
        'text': '''
今天天气真好，我们一起去海边玩吧。
大海真美，蓝蓝的天空，白白的云朵。
大家都非常开心，笑声不断传来。
        '''.strip()
    }

    # 进度回调
    async def progress_callback(step_type, message, progress_value, extra):
        print(f"[{progress_value*100:.0f}%] {step_type}: {message}")

    # 处理文案
    print("\n开始处理...")
    result = await processor.process_copywriting(
        test_copywriting,
        progress_callback
    )

    # 输出结果
    print("\n" + "=" * 60)
    print("处理结果:")
    print("=" * 60)
    print(f"成功: {result.get('success')}")
    print(f"视频URL: {result.get('video_url', 'N/A')}")
    print(f"场景数量: {result.get('scenes_count', 'N/A')}")
    print(f"总时长: {result.get('duration', 'N/A')}秒")

    if result.get('error'):
        print(f"错误: {result.get('error')}")

    return result


if __name__ == "__main__":
    result = asyncio.run(test_end_to_end())

    # 根据结果设置退出码
    sys.exit(0 if result.get('success') else 1)
