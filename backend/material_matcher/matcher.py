"""
素材匹配器
为场景匹配合适的视频素材
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path


class MaterialMatcher:
    """素材匹配器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化

        Args:
            config: {
                'local_path': 本地素材路径,
                'pexels_api_key': Pexels API密钥,
                'freepik_api_key': Freepik API密钥,
                'coverr_api_key': Coverr API密钥
            }
        """
        self.config = config
        self.local_path = config.get('local_path', '')
        self.pexels_api_key = config.get('pexels_api_key', '')
        self.freepik_api_key = config.get('freepik_api_key', '')
        self.coverr_api_key = config.get('coverr_api_key', '')

    async def batch_match_materials(
        self,
        scenes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        批量匹配素材

        Args:
            scenes: 场景列表

        Returns:
            更新后的场景列表
        """
        # 为每个场景匹配素材
        tasks = []
        for scene in scenes:
            task = self._match_material_for_scene(scene)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 更新场景
        for i, result in enumerate(results):
            if isinstance(result, str):
                scenes[i]['material'] = result
            elif isinstance(result, Exception):
                print(f"场景 {i+1} 素材匹配失败: {str(result)}")
                scenes[i]['material'] = None

        return scenes

    async def _match_material_for_scene(
        self,
        scene: Dict[str, Any]
    ) -> Optional[str]:
        """
        为单个场景匹配素材

        Args:
            scene: 场景数据

        Returns:
            素材文件路径
        """
        keywords = scene.get('keywords', [])

        # 1. 首先搜索本地素材
        local_material = self._search_local_material(keywords)
        if local_material:
            return local_material

        # 2. 如果本地没有，搜索网络素材
        # Pexels
        if self.pexels_api_key:
            pexels_material = await self._search_pexels(keywords)
            if pexels_material:
                return pexels_material

        # Freepik
        if self.freepik_api_key:
            freepik_material = await self._search_freepik(keywords)
            if freepik_material:
                return freepik_material

        # Coverr
        if self.coverr_api_key:
            coverr_material = await self._search_coverr(keywords)
            if coverr_material:
                return coverr_material

        # 都没有找到
        return None

    def _search_local_material(
        self,
        keywords: List[str]
    ) -> Optional[str]:
        """
        搜索本地素材

        Args:
            keywords: 关键词列表

        Returns:
            素材文件路径
        """
        if not self.local_path or not os.path.exists(self.local_path):
            return None

        # 支持的视频格式
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.webm']

        # 遍历本地素材目录
        try:
            for ext in video_extensions:
                # 简单匹配：查找文件名包含关键词的文件
                for keyword in keywords:
                    pattern = f"*{keyword}*{ext}"
                    matches = list(Path(self.local_path).glob(pattern))

                    if matches:
                        # 返回第一个匹配的文件
                        return str(matches[0])

            # 如果没有关键词匹配，返回任意一个视频文件
            for ext in video_extensions:
                matches = list(Path(self.local_path).glob(f"*{ext}"))
                if matches:
                    return str(matches[0])

        except Exception as e:
            print(f"搜索本地素材失败: {str(e)}")

        return None

    async def _search_pexels(
        self,
        keywords: List[str]
    ) -> Optional[str]:
        """
        搜索 Pexels 素材

        Args:
            keywords: 关键词列表

        Returns:
            素材URL
        """
        if not self.pexels_api_key:
            return None

        try:
            import aiohttp

            # 使用第一个关键词搜索
            keyword = keywords[0] if keywords else 'nature'

            url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=landscape"

            headers = {
                'Authorization': self.pexels_api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get('videos'):
                            # 获取第一个视频
                            video = data['videos'][0]
                            # 返回视频文件链接
                            video_files = video.get('video_files', [])
                            if video_files:
                                # 选择中等质量的视频
                                for vf in video_files:
                                    if vf.get('quality') == 'medium':
                                        return vf.get('link')
                                # 如果没有medium，返回第一个
                                return video_files[0].get('link')

        except Exception as e:
            print(f"Pexels 搜索失败: {str(e)}")

        return None

    async def _search_freepik(
        self,
        keywords: List[str]
    ) -> Optional[str]:
        """
        搜索 Freepik 素材

        Args:
            keywords: 关键词列表

        Returns:
            素材URL
        """
        if not self.freepik_api_key:
            return None

        # Freepik API 实现需要具体API文档
        # 这里返回占位符
        return None

    async def _search_coverr(
        self,
        keywords: List[str]
    ) -> Optional[str]:
        """
        搜索 Coverr 素材

        Args:
            keywords: 关键词列表

        Returns:
            素材URL
        """
        if not self.coverr_api_key:
            return None

        # Coverr API 实现需要具体API文档
        # 这里返回占位符
        return None

    async def download_material(
        self,
        url: str,
        output_path: str
    ) -> bool:
        """
        下载网络素材

        Args:
            url: 素材URL
            output_path: 输出路径

        Returns:
            是否成功
        """
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()

                        with open(output_path, 'wb') as f:
                            f.write(content)

                        return True
        except Exception as e:
            print(f"下载素材失败: {str(e)}")

        return False


# 测试代码
if __name__ == "__main__":
    async def test():
        config = {
            'local_path': './local_materials',
            'pexels_api_key': 'your_pexels_api_key'
        }

        matcher = MaterialMatcher(config)

        # 测试场景
        test_scenes = [
            {
                'index': 1,
                'text': '今天天气真好',
                'keywords': ['天气', '晴天', '阳光']
            }
        ]

        results = await matcher.batch_match_materials(test_scenes)

        for scene in results:
            print(f"场景 {scene['index']}: {scene.get('material', '未找到素材')}")

    asyncio.run(test())
