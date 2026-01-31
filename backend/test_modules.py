"""
模块功能测试
测试各个独立模块的功能
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_text_processor():
    """测试文本处理器"""
    print("\n" + "=" * 60)
    print("测试文本处理器")
    print("=" * 60)

    from text_processor.processor import TextProcessor

    processor = TextProcessor()

    test_text = """
    今天天气真好啊！我们一起去海边玩吧。
    大海真美，蓝蓝的天空，白白的云朵。
    大家都非常开心，笑声不断传来。
    """

    result = processor.process_copywriting(test_text)

    print(f"清理后文案: {result['cleaned_text']}")
    print(f"关键词: {result['keywords']}")
    print(f"场景数量: {len(result['scenes'])}")

    for scene in result['scenes']:
        print(f"\n场景 {scene['index']}:")
        print(f"  文本: {scene['text']}")
        print(f"  关键词: {scene['keywords']}")
        print(f"  预计时长: {scene['estimated_duration']:.1f}秒")


async def test_tts_generator():
    """测试TTS生成器"""
    print("\n" + "=" * 60)
    print("测试TTS生成器")
    print("=" * 60)

    from audio.tts_generator import TTSGenerator

    generator = TTSGenerator()

    if not generator.edge_tts_available:
        print("✗ edge-tts 未安装")
        print("请运行: pip install edge-tts")
        return

    # 测试生成
    test_text = "这是一个测试。"
    output_file = "./test_tts.mp3"

    print(f"生成音频: {test_text}")
    success = await generator.generate_audio(
        test_text,
        output_file,
        'zh-CN-XiaoxiaoNeural'
    )

    if success:
        print(f"✓ 音频已生成: {output_file}")
        duration = generator._get_audio_duration(output_file)
        print(f"  时长: {duration:.2f}秒")

        # 清理
        if os.path.exists(output_file):
            os.remove(output_file)
    else:
        print("✗ 音频生成失败")


async def test_material_matcher():
    """测试素材匹配器"""
    print("\n" + "=" * 60)
    print("测试素材匹配器")
    print("=" * 60)

    from material_matcher.matcher import MaterialMatcher

    config = {
        'local_path': './local_materials',
        'pexels_api_key': os.getenv('PEXELS_API_KEY', '')
    }

    matcher = MaterialMatcher(config)

    test_scenes = [
        {
            'index': 1,
            'text': '今天天气真好',
            'keywords': ['天气', '晴天', '阳光']
        }
    ]

    print("匹配素材...")
    results = await matcher.batch_match_materials(test_scenes)

    for scene in results:
        material = scene.get('material')
        if material:
            print(f"✓ 场景 {scene['index']}: {material}")
        else:
            print(f"✗ 场景 {scene['index']}: 未找到素材")


async def test_video_editor():
    """测试视频编辑器"""
    print("\n" + "=" * 60)
    print("测试视频编辑器")
    print("=" * 60)

    from video_editor.editor import VideoEditor

    editor = VideoEditor()

    if not editor.ffmpeg_available:
        print("✗ FFmpeg 未安装")
        print("请从 https://ffmpeg.org 下载安装")
        return

    print("✓ FFmpeg 可用")

    # 测试获取视频信息
    # 这里需要有一个测试视频文件


async def test_oss_uploader():
    """测试OSS上传器"""
    print("\n" + "=" * 60)
    print("测试OSS上传器")
    print("=" * 60)

    from storage.oss_uploader import OSSUploader

    config = {
        'access_key_id': os.getenv('OSS_ACCESS_KEY_ID', ''),
        'access_key_secret': os.getenv('OSS_ACCESS_KEY_SECRET', ''),
        'bucket_name': os.getenv('OSS_BUCKET_NAME', ''),
        'endpoint': os.getenv('OSS_ENDPOINT', '')
    }

    uploader = OSSUploader(config)

    if uploader.is_configured():
        print("✓ OSS 已配置")
        print(f"  Bucket: {config['bucket_name']}")
        print(f"  Endpoint: {config['endpoint']}")
    else:
        print("✗ OSS 未配置")
        print("请设置环境变量:")
        print("  OSS_ACCESS_KEY_ID")
        print("  OSS_ACCESS_KEY_SECRET")
        print("  OSS_BUCKET_NAME")
        print("  OSS_ENDPOINT")


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("模块功能测试")
    print("=" * 60)

    await test_text_processor()
    await test_tts_generator()
    await test_material_matcher()
    await test_video_editor()
    await test_oss_uploader()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
