"""
TTS音频生成器
使用Edge TTS生成语音
"""
import os
import asyncio
import subprocess
from typing import List, Dict, Any, Optional
import tempfile


class TTSGenerator:
    """TTS音频生成器"""

    def __init__(self, output_dir: str = "./output/audio"):
        """
        初始化

        Args:
            output_dir: 音频输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Edge-TTS 可用性
        self.edge_tts_available = self._check_edge_tts()

        # 默认语音
        self.voices = {
            'female': 'zh-CN-XiaoxiaoNeural',  # 女声
            'male': 'zh-CN-YunyangNeural',      # 男声
            'female2': 'zh-CN-XiaoyiNeural',    # 女声2
            'male2': 'zh-CN-YunxiNeural'        # 男声2
        }

    def _check_edge_tts(self) -> bool:
        """检查 edge-tts 是否可用"""
        try:
            result = subprocess.run(['edge-tts', '--version'],
                                  capture_output=True,
                                  timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def generate_audio(
        self,
        text: str,
        output_file: str,
        voice: str = 'zh-CN-XiaoxiaoNeural'
    ) -> bool:
        """
        生成单条音频

        Args:
            text: 文本内容
            output_file: 输出文件路径
            voice: 语音类型

        Returns:
            是否成功
        """
        if not self.edge_tts_available:
            print("edge-tts 不可用")
            return False

        try:
            # 使用 edge-tts 生成音频
            cmd = [
                'edge-tts',
                '--text', text,
                '--voice', voice,
                '--write-media', output_file
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5分钟超时
            )

            return process.returncode == 0 and os.path.exists(output_file)

        except asyncio.TimeoutError:
            print(f"TTS 生成超时: {text[:50]}")
            return False
        except Exception as e:
            print(f"TTS 生成失败: {str(e)}")
            return False

    async def batch_generate_audio(
        self,
        scenes: List[Dict[str, Any]],
        voice: str = 'female'
    ) -> List[Dict[str, Any]]:
        """
        批量生成场景音频

        Args:
            scenes: 场景列表
            voice: 语音类型 (female/male)

        Returns:
            更新后的场景列表
        """
        # 获取语音ID
        voice_id = self.voices.get(voice, self.voices['female'])

        # 创建任务列表
        tasks = []
        for scene in scenes:
            text = scene.get('text', '')
            if text:
                # 生成音频文件名
                audio_file = os.path.join(
                    self.output_dir,
                    f"scene_{scene['index']}.mp3"
                )

                # 创建任务
                task = self._generate_and_update(scene, audio_file, voice_id)
                tasks.append(task)

        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"场景 {i+1} 音频生成失败: {str(result)}")

        return scenes

    async def _generate_and_update(
        self,
        scene: Dict[str, Any],
        audio_file: str,
        voice_id: str
    ) -> Dict[str, Any]:
        """
        生成音频并更新场景

        Args:
            scene: 场景数据
            audio_file: 音频文件路径
            voice_id: 语音ID

        Returns:
            更新后的场景
        """
        text = scene.get('text', '')

        # 生成音频
        success = await self.generate_audio(text, audio_file, voice_id)

        if success and os.path.exists(audio_file):
            # 更新场景信息
            scene['audio_path'] = audio_file

            # 获取音频时长
            duration = self._get_audio_duration(audio_file)
            if duration:
                scene['actual_duration'] = duration

        return scene

    def _get_audio_duration(self, audio_file: str) -> Optional[float]:
        """
        获取音频时长

        Args:
            audio_file: 音频文件路径

        Returns:
            音频时长（秒）
        """
        try:
            # 使用 ffprobe 获取时长
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_file
            ]

            result = subprocess.run(cmd,
                                   capture_output=True,
                                   text=True,
                                   timeout=10)

            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration
        except Exception as e:
            print(f"获取音频时长失败: {str(e)}")

        return None

    def get_available_voices(self) -> Dict[str, str]:
        """
        获取可用的语音列表

        Returns:
            语音字典
        """
        return self.voices.copy()


# 测试代码
if __name__ == "__main__":
    async def test():
        generator = TTSGenerator()

        print(f"edge-tts 可用: {generator.edge_tts_available}")

        # 测试生成音频
        if generator.edge_tts_available:
            output_file = "./test_audio.mp3"
            success = await generator.generate_audio(
                "你好，这是一个测试。",
                output_file
            )
            print(f"生成结果: {success}")

            if success:
                duration = generator._get_audio_duration(output_file)
                print(f"音频时长: {duration}秒")

    asyncio.run(test())
