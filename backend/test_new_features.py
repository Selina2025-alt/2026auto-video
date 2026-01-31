"""
新功能测试
测试新添加的功能
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_websocket_message_format():
    """测试WebSocket消息格式"""
    print("=" * 60)
    print("测试WebSocket消息格式")
    print("=" * 60)

    # 模拟视频完成消息
    video_completed_msg = {
        'type': 'video_completed',
        'video': {
            'url': 'https://example.com/video.mp4',
            'preview_url': '/output/test_user/videos/test.mp4',
            'is_local': False,
            'title': '测试视频标题',
            'record_id': 'rec_001',
            'index': 1
        }
    }

    print("video_completed 消息格式:")
    import json
    print(json.dumps(video_completed_msg, indent=2, ensure_ascii=False))

    # 模拟步骤消息
    step_msg = {
        'type': 'step',
        'step_name': '正在生成配音',
        'message': '使用 AI 语音合成技术生成配音...',
        'details': {
            'step_number': 9,
            'total_steps': 14,
            'progress': 60
        }
    }

    print("\nstep 消息格式:")
    print(json.dumps(step_msg, indent=2, ensure_ascii=False))


async def test_local_video_preview():
    """测试本地视频预览"""
    print("\n" + "=" * 60)
    print("测试本地视频预览")
    print("=" * 60)

    # 模拟本地视频
    local_video = {
        'url': 'file:///d:/videos/test.mp4',
        'preview_url': '/output/user123/videos/test_001.mp4',
        'is_local': True
    }

    print(f"本地视频URL: {local_video['url']}")
    print(f"预览URL: {local_video['preview_url']}")
    print(f"完整预览地址: http://localhost:8001{local_video['preview_url']}")


async def test_config_compatibility():
    """测试配置兼容性"""
    print("\n" + "=" * 60)
    print("测试配置兼容性")
    print("=" * 60)

    # 测试旧格式配置
    old_config = {
        'output': {
            'ossAccessKeyId': 'old_key_id',
            'ossAccessKeySecret': 'old_secret',
            'ossBucketName': 'old_bucket',
            'ossEndpoint': 'oss-cn-hangzhou.aliyuncs.com'
        }
    }

    # 测试新格式配置
    new_config = {
        'output': {
            'access_key_id': 'new_key_id',
            'access_key_secret': 'new_secret',
            'bucket_name': 'new_bucket',
            'endpoint': 'oss-cn-hangzhou.aliyuncs.com'
        }
    }

    from processor.video_processor import VideoProcessor

    print("旧格式配置:")
    processor_old = VideoProcessor(old_config)
    print(f"  OSS配置: {processor_old.oss_uploader is not None}")

    print("\n新格式配置:")
    processor_new = VideoProcessor(new_config)
    print(f"  OSS配置: {processor_new.oss_uploader is not None}")


async def test_progress_steps():
    """测试进度步骤"""
    print("\n" + "=" * 60)
    print("测试14步进度流程")
    print("=" * 60)

    steps = [
        "正在读取您的文案内容",
        "正在整理和优化文案",
        "正在拆分成多个镜头",
        "正在提取场景关键词",
        "正在本地素材库中查找",
        "正在网络上搜索视频素材",
        "继续搜索更多素材",
        "正在寻找补充素材",
        "正在生成配音",
        "正在生成字幕",
        "正在剪辑合成视频",
        "正在优化视频质量",
        "正在上传到云端",
        "正在保存结果"
    ]

    for i, step in enumerate(steps, 1):
        progress = round((i / len(steps)) * 100)
        print(f"步骤 {i}/14 ({progress}%): {step}")


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("新功能测试")
    print("=" * 60)

    await test_websocket_message_format()
    await test_local_video_preview()
    await test_config_compatibility()
    await test_progress_steps()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
