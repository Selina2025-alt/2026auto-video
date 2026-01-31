"""
飞书表格操作处理器
"""
from typing import List, Dict, Any
from .client import FeishuClient

class TableHandler:
    """飞书表格处理器"""
    
    def __init__(self, client: FeishuClient, base_token: str, table_id: str):
        self.client = client
        self.base_token = base_token
        self.table_id = table_id
    
    def get_all_copywriting(self) -> List[Dict[str, Any]]:
        """
        获取所有原文案
        
        Returns:
            包含原文案的记录列表
        """
        records = self.client.get_records(self.base_token, self.table_id)
        return records
    
    def update_video_result(self, record_id: str, video_url: str, status: str = "✅ 已完成"):
        """
        更新视频结果
        
        Args:
            record_id: 记录ID
            video_url: 视频链接
            status: 状态
        """
        fields = {
            "产出视频": video_url,
            "状态": status
        }
        return self.client.update_record(self.base_token, self.table_id, record_id, fields)
    
    def update_status(self, record_id: str, status: str):
        """
        更新状态
        
        Args:
            record_id: 记录ID
            status: 状态
        """
        fields = {"状态": status}
        return self.client.update_record(self.base_token, self.table_id, record_id, fields)
