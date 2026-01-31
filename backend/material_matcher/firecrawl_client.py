"""
Firecrawl客户端
用于网页内容抓取
"""
import os
from typing import Dict, Any, Optional, List


class FirecrawlClient:
    """Firecrawl客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化

        Args:
            api_key: Firecrawl API密钥
        """
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        self.base_url = "https://api.firecrawl.dev/v1"

    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_key)

    async def scrape_url(
        self,
        url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        抓取网页内容

        Args:
            url: 网页URL
            options: 抓取选项

        Returns:
            抓取结果
        """
        if not self.is_configured():
            print("Firecrawl 未配置")
            return None

        try:
            import aiohttp

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'url': url,
                **(options or {})
            }

            scrape_url = f"{self.base_url}/scrape"

            async with aiohttp.ClientSession() as session:
                async with session.post(scrape_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        print(f"Firecrawl 抓取失败: {error_text}")

        except Exception as e:
            print(f"Firecrawl 抓取异常: {str(e)}")

        return None

    async def batch_scrape(
        self,
        urls: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量抓取网页

        Args:
            urls: 网页URL列表
            options: 抓取选项

        Returns:
            抓取结果列表
        """
        results = []

        for url in urls:
            result = await self.scrape_url(url, options)
            results.append(result or {})

        return results

    async def crawl(
        self,
        url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        爬取网站

        Args:
            url: 起始URL
            options: 爬取选项

        Returns:
            爬取任务ID
        """
        if not self.is_configured():
            print("Firecrawl 未配置")
            return None

        try:
            import aiohttp

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'url': url,
                **(options or {})
            }

            crawl_url = f"{self.base_url}/crawl"

            async with aiohttp.ClientSession() as session:
                async with session.post(crawl_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('id')
                    else:
                        error_text = await response.text()
                        print(f"Firecrawl 爬取失败: {error_text}")

        except Exception as e:
            print(f"Firecrawl 爬取异常: {str(e)}")

        return None

    async def get_crawl_status(
        self,
        crawl_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取爬取任务状态

        Args:
            crawl_id: 爬取任务ID

        Returns:
            任务状态
        """
        if not self.is_configured():
            return None

        try:
            import aiohttp

            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }

            status_url = f"{self.base_url}/crawl/{crawl_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(status_url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()

        except Exception as e:
            print(f"获取爬取状态失败: {str(e)}")

        return None

    async def search(
        self,
        query: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        搜索网页

        Args:
            query: 搜索查询
            options: 搜索选项

        Returns:
            搜索结果
        """
        if not self.is_configured():
            return None

        try:
            import aiohttp

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'query': query,
                **(options or {})
            }

            search_url = f"{self.base_url}/search"

            async with aiohttp.ClientSession() as session:
                async with session.post(search_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        print(f"Firecrawl 搜索失败: {error_text}")

        except Exception as e:
            print(f"Firecrawl 搜索异常: {str(e)}")

        return None


# 测试代码
if __name__ == "__main__":
    async def test():
        client = FirecrawlClient()

        if client.is_configured():
            # 测试抓取
            result = await client.scrape_url("https://example.com")
            print(f"抓取结果: {result}")
        else:
            print("Firecrawl 未配置，请设置 API 密钥")

    import asyncio
    asyncio.run(test())
