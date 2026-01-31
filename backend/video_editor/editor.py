"""
视频编辑器
处理视频剪辑、拼接、添加字幕等
"""
import os
import subprocess
from typing import List, Dict, Any, Optional
import asyncio


class VideoEditor:
    """视频编辑器"""

    def __init__(self, output_dir: str = "./output/videos"):
        """
        初始化

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 检查 ffmpeg 是否可用
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """检查 ffmpeg 是否可用"""
        try:
            result = subprocess.run(['ffmpeg', '-version'],
                                  capture_output=True,
                                  timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run_ffmpeg(self, args: List[str], timeout: int = 300) -> bool:
        """
        运行 ffmpeg 命令

        Args:
            args: ffmpeg 参数列表
            timeout: 超时时间

        Returns:
            是否成功
        """
        if not self.ffmpeg_available:
            print("ffmpeg 不可用")
            return False

        try:
            cmd = ['ffmpeg'] + args
            result = subprocess.run(cmd,
                                   capture_output=True,
                                   timeout=timeout)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"ffmpeg 命令超时")
            return False
        except Exception as e:
            print(f"ffmpeg 执行失败: {str(e)}")
            return False

    async def compose_scene_video(
        self,
        scene: Dict[str, Any],
        scene_index: int,
        temp_dir: Optional[str] = None
    ) -> Optional[str]:
        """
        合成单个场景视频

        Args:
            scene: 场景数据
            scene_index: 场景索引
            temp_dir: 临时目录

        Returns:
            输出视频路径，失败返回 None
        """
        if not self.ffmpeg_available:
            print("ffmpeg 不可用，无法合成视频")
            return None

        # 获取场景参数
        text = scene.get('text', '')
        duration = scene.get('actual_duration', scene.get('estimated_duration', 5))
        material_path = scene.get('material')

        # 如果有素材文件，使用素材；否则创建纯色背景
        if material_path and os.path.exists(material_path):
            input_video = material_path
        else:
            # 创建一个纯色背景视频（使用 color=c 参数）
            # 先创建一个临时视频文件
            temp_bg = os.path.join(temp_dir or '', f'bg_{scene_index}.mp4')
            bg_args = [
                '-f', 'lavfi',
                '-i', f'color=c=blue:s=1920x1080:d={duration}',
                '-c:v', 'libx264',
                '-t', str(duration),
                '-pix_fmt', 'yuv420p',
                temp_bg
            ]
            if self._run_ffmpeg(bg_args):
                input_video = temp_bg
            else:
                return None

        # 输出路径
        output_path = os.path.join(
            temp_dir or self.output_dir,
            f'scene_{scene_index}.mp4'
        )

        # 如果有音频，合并音频和视频
        audio_path = scene.get('audio_path')
        if audio_path and os.path.exists(audio_path):
            args = [
                '-i', input_video,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                '-y',
                output_path
            ]
        else:
            # 只处理视频，调整时长
            args = [
                '-i', input_video,
                '-t', str(duration),
                '-c:v', 'copy',
                '-y',
                output_path
            ]

        success = self._run_ffmpeg(args)

        # 清理临时背景文件
        if material_path is None and os.path.exists(temp_bg):
            os.remove(temp_bg)

        return output_path if success else None

    async def concatenate_videos(
        self,
        video_paths: List[str],
        output_path: str
    ) -> bool:
        """
        拼接多个视频

        Args:
            video_paths: 视频文件路径列表
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        if not self.ffmpeg_available:
            return False

        if not video_paths:
            return False

        # 创建文件列表
        list_file = output_path + '.txt'
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for path in video_paths:
                    # 转义路径中的特殊字符
                    safe_path = path.replace('\\', '/').replace("'", "\\'")
                    f.write(f"file '{safe_path}'\n")

            # 使用 concat demuxer 拼接
            args = [
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                '-y',
                output_path
            ]

            success = self._run_ffmpeg(args)

            # 清理临时文件
            if os.path.exists(list_file):
                os.remove(list_file)

            return success

        except Exception as e:
            print(f"拼接视频失败: {str(e)}")
            if os.path.exists(list_file):
                os.remove(list_file)
            return False

    async def add_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str
    ) -> bool:
        """
        添加字幕到视频

        Args:
            video_path: 输入视频路径
            subtitle_path: 字幕文件路径 (SRT格式)
            output_path: 输出视频路径

        Returns:
            是否成功
        """
        if not self.ffmpeg_available:
            return False

        # 使用 subtitles filter 添加字幕
        args = [
            '-i', video_path,
            '-vf', f"subtitles='{subtitle_path}'",
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        return self._run_ffmpeg(args)

    async def add_background_music(
        self,
        video_path: str,
        music_path: str,
        output_path: str,
        music_volume: float = 0.3
    ) -> bool:
        """
        添加背景音乐

        Args:
            video_path: 输入视频路径
            music_path: 音乐文件路径
            output_path: 输出视频路径
            music_volume: 音乐音量 (0.0 - 1.0)

        Returns:
            是否成功
        """
        if not self.ffmpeg_available:
            return False

        # 计算音量衰减
        volume_filter = f'volume={music_volume}'

        # 使用 amix 混合音频
        args = [
            '-i', video_path,
            '-i', music_path,
            '-filter_complex',
            f'[1:a]{volume_filter}[a1];[0:a][a1]amix=inputs=2:duration=first',
            '-c:v', 'copy',
            '-y',
            output_path
        ]

        return self._run_ffmpeg(args)

    async def resize_video(
        self,
        video_path: str,
        output_path: str,
        width: int = 1920,
        height: int = 1080
    ) -> bool:
        """
        调整视频分辨率

        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            width: 目标宽度
            height: 目标高度

        Returns:
            是否成功
        """
        if not self.ffmpeg_available:
            return False

        args = [
            '-i', video_path,
            '-vf', f'scale={width}:{height}',
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        return self._run_ffmpeg(args)

    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        获取视频信息

        Args:
            video_path: 视频文件路径

        Returns:
            视频信息字典
        """
        if not self.ffmpeg_available:
            return None

        try:
            # 使用 ffprobe 获取视频信息
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]

            result = subprocess.run(cmd,
                                   capture_output=True,
                                   text=True,
                                   timeout=10)

            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)

                # 提取关键信息
                video_stream = next(
                    (s for s in info.get('streams', []) if s.get('codec_type') == 'video'),
                    None
                )
                audio_stream = next(
                    (s for s in info.get('streams', []) if s.get('codec_type') == 'audio'),
                    None
                )

                return {
                    'duration': float(info.get('format', {}).get('duration', 0)),
                    'width': int(video_stream.get('width', 0)) if video_stream else 0,
                    'height': int(video_stream.get('height', 0)) if video_stream else 0,
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
                    'has_audio': audio_stream is not None
                }
        except Exception as e:
            print(f"获取视频信息失败: {str(e)}")

        return None


# 测试代码
if __name__ == "__main__":
    async def test():
        editor = VideoEditor()

        print(f"ffmpeg 可用: {editor.ffmpeg_available}")

        # 测试场景合成
        test_scene = {
            'text': '这是一个测试场景',
            'estimated_duration': 5,
            'actual_duration': 5,
            'material': None,
            'audio_path': None
        }

        # output_path = await editor.compose_scene_video(test_scene, 1)
        # print(f"输出路径: {output_path}")

    asyncio.run(test())
