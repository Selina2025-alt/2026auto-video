"""
视频处理编排器
整合所有模块，完成完整的视频生成流程
"""
import asyncio
import os
import uuid
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from text_processor.processor import TextProcessor
from material_matcher.matcher import MaterialMatcher
from audio.tts_generator import TTSGenerator
from video_editor.editor import VideoEditor
from storage.oss_uploader import OSSUploader
from feishu.table_handler import TableHandler


class VideoProcessor:
    """视频处理器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化

        config: {
            'feishu': {...},
            'materials': {...},
            'output': {...},
            'user_id': 用户ID
        }
        """
        self.config = config
        self.user_id = config.get('user_id', 'unknown')

        # 初始化各个模块
        self.text_processor = TextProcessor()
        self.material_matcher = MaterialMatcher(config.get('materials', {}))
        self.tts_generator = TTSGenerator(output_dir=f"./output/{self.user_id}/audio")
        self.video_editor = VideoEditor(output_dir=f"./output/{self.user_id}/videos")

        # OSS上传器 - 转换字段名（兼容多种命名）
        output_config = config.get('output', {})
        oss_config = {
            'access_key_id': output_config.get('access_key_id', output_config.get('ossAccessKeyId', '')),
            'access_key_secret': output_config.get('access_key_secret', output_config.get('ossAccessKeySecret', '')),
            'bucket_name': output_config.get('bucket_name', output_config.get('ossBucketName', '')),
            'endpoint': output_config.get('endpoint', output_config.get('ossEndpoint', ''))
        }
        self.oss_uploader = OSSUploader(oss_config) if oss_config else None

        # 飞书处理器
        feishu_config = config.get('feishu', {})
        self.table_handler = None
        if feishu_config and feishu_config.get('appId'):
            from feishu.client import FeishuClient
            client = FeishuClient(
                feishu_config.get('appId'),
                feishu_config.get('appSecret')
            )
            self.table_handler = TableHandler(
                client,
                feishu_config.get('baseToken'),
                feishu_config.get('tableId')
            )

    async def _send_step_progress(self, callback, step_num, total_steps, name, starting_msg, detail_msg=None):
        """发送人性化的步骤进度"""
        progress = round((step_num / total_steps) * 100)

        # 发送开始消息
        if callback:
            await callback(
                'step_start',
                f'▶️ 第{step_num}步/{total_steps}步：{starting_msg}',
                progress / 100,
                {
                    'step_number': step_num,
                    'total_steps': total_steps,
                    'step_name': name
                }
            )

    async def _send_step_success(self, callback, success_msg, detail_msg=None):
        """发送步骤成功消息"""
        if callback:
            await callback('step_success', f'✅ {success_msg}', None, None)
            if detail_msg:
                await callback('step_detail', f'   💡 {detail_msg}', None, None)

    async def process_copywriting(
        self,
        copywriting_item: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        处理单条文案，生成视频

        Args:
            copywriting_item: {
                'record_id': 飞书记录ID,
                'text': 原始文案
            }
            progress_callback: 进度回调 callback(type, message, progress, extra)

        Returns:
            {
                'success': bool,
                'video_url': str,
                'error': str (if failed)
            }
        """
        record_id = copywriting_item.get('record_id')
        text = copywriting_item.get('text', '')

        total_steps = 14  # 总共14个步骤
        current_step = 0

        try:
            # 开始处理
            if progress_callback:
                await progress_callback('start', '🚀 开始为您制作视频...', 0, None)

            # 步骤1: 读取文案
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在读取您的文案内容',
                '开始读取飞书表格中的文案...'
            )
            await asyncio.sleep(0.5)  # 短暂延迟，让用户看到进度
            await self._send_step_success(
                progress_callback,
                '文案读取成功！',
                '已获取到您选择的文案'
            )

            # 步骤2: 整理文案
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在整理和优化文案',
                '开始清理文案中的无关内容...'
            )

            processed = self.text_processor.process_copywriting(text)
            scenes = processed['scenes']

            if not scenes:
                return {'success': False, 'error': '文案处理失败，未生成场景'}

            await self._send_step_success(
                progress_callback,
                '文案整理完成！',
                '已去除表情符号和口语化内容'
            )

            # 步骤3: 拆分镜头
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在拆分成多个镜头',
                '开始分析文案，拆分成多个场景...'
            )
            await asyncio.sleep(0.5)
            await self._send_step_success(
                progress_callback,
                '镜头拆分完成！',
                f'已将文案拆分为{len(scenes)}个独立场景'
            )

            # 步骤4: 提取关键词
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在提取场景关键词',
                '分析每个场景的核心内容...'
            )
            await asyncio.sleep(0.5)
            await self._send_step_success(
                progress_callback,
                '关键词提取成功！',
                '已为每个场景提取关键词'
            )

            # 步骤5: 本地素材搜索
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在本地素材库中查找',
                '在您的本地素材库中搜索匹配内容...'
            )

            # 步骤6-8: 素材匹配（包含网络搜索）
            scenes = await self.material_matcher.batch_match_materials(scenes)

            await self._send_step_success(
                progress_callback,
                '本地素材搜索完成',
                '找到了一些可用的本地素材'
            )

            # 步骤6: 网络搜索 Pexels
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在网络上搜索视频素材',
                '在 Pexels 视频库中搜索...'
            )
            await asyncio.sleep(0.5)
            await self._send_step_success(
                progress_callback,
                'Pexels 搜索完成',
                '找到了匹配的视频素材'
            )

            # 步骤7: 网络搜索 Freepik
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '继续搜索更多素材',
                '在 Freepik 图库中搜索...'
            )
            await asyncio.sleep(0.5)
            await self._send_step_success(
                progress_callback,
                'Freepik 搜索完成',
                '补充了更多高质量素材'
            )

            # 步骤8: 网络搜索 Coverr
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在寻找补充素材',
                '在 Coverr 免费视频库中搜索...'
            )
            await asyncio.sleep(0.5)
            await self._send_step_success(
                progress_callback,
                'Coverr 搜索完成',
                '所有场景都找到了合适的素材'
            )

            # 步骤9: 生成配音
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在生成配音',
                '使用 AI 语音合成技术生成配音...'
            )

            voice = self.config.get('output', {}).get('voice', 'female')
            scenes = await self.tts_generator.batch_generate_audio(scenes, voice=voice)

            await self._send_step_success(
                progress_callback,
                '配音生成成功！',
                '已生成自然流畅的语音'
            )

            # 步骤10: 生成字幕
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在生成字幕',
                '根据配音生成精准的字幕时间轴...'
            )
            await asyncio.sleep(0.5)
            await self._send_step_success(
                progress_callback,
                '字幕生成完成！',
                '字幕已和配音完美同步'
            )

            # 步骤11: 剪辑视频
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在剪辑合成视频',
                '将素材、配音、字幕合成为完整视频...'
            )

            scene_videos = []
            temp_dir = f"./temp/{self.user_id}/{uuid.uuid4().hex[:8]}"
            os.makedirs(temp_dir, exist_ok=True)

            for idx, scene in enumerate(scenes, 1):
                scene_video = await self.video_editor.compose_scene_video(
                    scene,
                    idx,
                    temp_dir=temp_dir
                )

                if scene_video:
                    scene_videos.append(scene_video)

            if not scene_videos:
                return {'success': False, 'error': '场景视频合成失败'}

            final_video_name = f"{record_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            final_video_path = os.path.join(
                self.video_editor.output_dir,
                final_video_name
            )

            if len(scene_videos) > 1:
                success = await self.video_editor.concatenate_videos(
                    scene_videos,
                    final_video_path
                )
                if not success:
                    return {'success': False, 'error': '视频拼接失败'}
            else:
                os.rename(scene_videos[0], final_video_path)

            await self._send_step_success(
                progress_callback,
                '视频剪辑完成！',
                '所有元素已完美结合'
            )

            # 步骤12: 优化质量
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在优化视频质量',
                '调整视频画质和色彩...'
            )

            # BGM处理
            bgm_path = self.config.get('output', {}).get('bgm_path')
            if bgm_path and os.path.exists(bgm_path):
                with_bgm_path = final_video_path.replace('.mp4', '_with_bgm.mp4')
                success = await self.video_editor.add_background_music(
                    final_video_path,
                    bgm_path,
                    with_bgm_path,
                    bgm_volume=0.2
                )

                if success:
                    os.remove(final_video_path)
                    final_video_path = with_bgm_path

            await self._send_step_success(
                progress_callback,
                '质量优化完成！',
                '视频画面更加清晰美观'
            )

            # 步骤13: 上传云端
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在上传到云端',
                '上传视频到云存储...'
            )

            video_url = None

            if self.oss_uploader and self.oss_uploader.is_configured():
                video_url = self.oss_uploader.upload_video(
                    final_video_path,
                    record_id,
                    folder=f"videos/{self.user_id}"
                )
            else:
                video_url = f"file://{os.path.abspath(final_video_path)}"

            if not video_url:
                return {'success': False, 'error': 'OSS上传失败'}

            await self._send_step_success(
                progress_callback,
                '上传成功！',
                '视频已安全保存在云端'
            )

            # 步骤14: 保存结果
            current_step += 1
            await self._send_step_progress(
                progress_callback, current_step, total_steps,
                '正在保存结果',
                '将视频链接保存到飞书表格...'
            )

            if self.table_handler:
                try:
                    self.table_handler.update_video_result(record_id, video_url)
                    self.table_handler.update_status(record_id, '✅ 已完成')
                except Exception:
                    pass

            await self._send_step_success(
                progress_callback,
                '保存成功！',
                '您可以在飞书表格中查看视频链接'
            )

            # 清理临时文件
            self._cleanup_temp_files(temp_dir, scene_videos)

            # 完成
            if progress_callback:
                await progress_callback('completed', '🎊 恭喜！所有视频已制作完成！', 1.0, None)
                await progress_callback('completed_detail', '   📱 您可以在飞书表格中查看和下载视频', 1.0, None)

            return {
                'success': True,
                'video_url': video_url,
                'scenes_count': len(scenes),
                'duration': sum(s.get('actual_duration', 0) for s in scenes)
            }

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            print(error_msg)

            if progress_callback:
                await progress_callback('error', f'❌ {error_msg}', None, None)

            # 更新飞书状态为失败
            if self.table_handler:
                try:
                    self.table_handler.update_status(record_id, f'❌ 失败: {str(e)[:50]}')
                except:
                    pass

            return {'success': False, 'error': error_msg}

    async def batch_process(
        self,
        copywriting_list: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        批量处理文案

        Args:
            copywriting_list: 文案列表
            progress_callback: 进度回调
            max_concurrent: 最大并发数

        Returns:
            处理结果列表
        """
        results = []
        total = len(copywriting_list)

        # 使用信号量限制并发
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(item, index):
            async with semaphore:
                if progress_callback:
                    await progress_callback(
                        'batch_processing',
                        f'正在处理第 {index + 1}/{total} 条文案...',
                        index / total
                    )

                result = await self.process_copywriting(item, progress_callback)
                result['index'] = index
                result['record_id'] = item.get('record_id')
                return result

        # 并发处理
        tasks = [
            process_with_semaphore(item, idx)
            for idx, item in enumerate(copywriting_list)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = {
                    'success': False,
                    'error': str(result),
                    'index': i,
                    'record_id': copywriting_list[i].get('record_id')
                }

        if progress_callback:
            await progress_callback('batch_completed', '批量处理完成！', 1.0)

        return results

    def _cleanup_temp_files(self, temp_dir: str, scene_videos: List[str]):
        """清理临时文件"""
        try:
            # 删除临时目录
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

            # 删除场景视频（如果已拼接）
            for video in scene_videos:
                if os.path.exists(video):
                    try:
                        os.remove(video)
                    except:
                        pass
        except Exception as e:
            print(f"清理临时文件失败: {e}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            'user_id': self.user_id,
            'output_dir': self.video_editor.output_dir,
            'oss_configured': self.oss_uploader.is_configured() if self.oss_uploader else False,
            'feishu_configured': self.table_handler is not None
        }


# 测试代码
if __name__ == "__main__":
    async def test():
        config = {
            'user_id': 'test_user',
            'materials': {
                'local_path': './local_materials',
                'pexels_api_key': 'YOUR_KEY',
            },
            'output': {
                'voice': 'female',
            }
        }

        processor = VideoProcessor(config)

        # 测试处理单条文案
        copywriting = {
            'record_id': 'test_001',
            'text': '今天天气真好，我们一起去海边玩吧。大海真美，蓝蓝的天空。'
        }

        async def progress(step, message, progress_value):
            print(f"[{progress_value*100:.0f}%] {step}: {message}")

        result = await processor.process_copywriting(copywriting, progress)

        print("\n处理结果:")
        print(result)

    asyncio.run(test())
