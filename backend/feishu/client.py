"""
飞书API客户端
负责与飞书开放平台交互
"""
import requests
import time
from typing import Dict, Any, Optional

class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token: Optional[str] = None
        self.token_expire_time: int = 0
        self.base_url = "https://open.feishu.cn/open-apis"
    
    def get_tenant_access_token(self) -> str:
        """获取tenant_access_token"""
        # 检查token是否过期
        if self.tenant_access_token and time.time() < self.token_expire_time:
            return self.tenant_access_token
        
        # 获取新token - 使用tenant_access_token（企业自建应用）
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            # 打印调试信息
            print(f"请求URL: {url}")
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"响应内容: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            print(f"响应数据: {data}")
            
            if data.get('code') == 0:
                self.tenant_access_token = data['tenant_access_token']
                # 提前5分钟过期
                self.token_expire_time = time.time() + data['expire'] - 300
                return self.tenant_access_token
            else:
                error_msg = data.get('msg', '未知错误')
                raise Exception(f"获取token失败: {error_msg} (code: {data.get('code')})")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.get_tenant_access_token()}",
            "Content-Type": "application/json"
        }
    
    def get_records(self, base_token: str, table_id: str, 
                    page_size: int = 100) -> list:
        """
        获取多维表格记录
        
        Args:
            base_token: 多维表格base token
            table_id: 表格ID
            page_size: 每页记录数
        
        Returns:
            记录列表
        """
        url = f"{self.base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/records"
        params = {"page_size": page_size}
        
        all_records = []
        has_more = True
        page_token = None
        
        try:
            while has_more:
                if page_token:
                    params['page_token'] = page_token
                
                print(f"请求URL: {url}")
                print(f"请求参数: {params}")
                
                response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
                
                print(f"响应状态码: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"响应内容: {response.text}")
                
                response.raise_for_status()
                
                data = response.json()
                # print(f"响应数据: {data}")  # 注释掉避免emoji编码问题
                print(f"[OK] 成功获取到 {len(data.get('data', {}).get('items', []))} 条记录")
                
                if data.get('code') == 0:
                    records = data['data']['items']
                    all_records.extend(records)
                    has_more = data['data'].get('has_more', False)
                    page_token = data['data'].get('page_token')
                else:
                    error_msg = data.get('msg', '未知错误')
                    raise Exception(f"获取记录失败: {error_msg} (code: {data.get('code')})")
            
            return all_records
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
    
    def update_record(self, base_token: str, table_id: str, 
                     record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新记录
        
        Args:
            base_token: 多维表格base token
            table_id: 表格ID
            record_id: 记录ID
            fields: 要更新的字段
        
        Returns:
            更新后的记录
        """
        url = f"{self.base_url}/bitable/v1/apps/{base_token}/tables/{table_id}/records/{record_id}"
        payload = {"fields": fields}
        
        response = requests.put(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get('code') == 0:
            return data['data']['record']
        else:
            raise Exception(f"更新记录失败: {data.get('msg')}")
