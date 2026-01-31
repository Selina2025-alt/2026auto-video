"""
配置文件管理模块
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """从YAML文件加载配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # 创建默认配置
            self.config = self.get_default_config()
            self.save_config()
    
    def save_config(self):
        """保存配置到YAML文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'feishu': {
                'app_id': '',
                'app_secret': '',
                'base_token': '',
                'table_id': ''
            },
            'material_apis': {
                'pexels': '',
                'freepik': '',
                'coverr': '',
                'firecrawl': ''
            },
            'ai_video': {
                'mode': 'skip',
                'tools': [],
                'proxy': {
                    'base_url': '',
                    'api_key': ''
                }
            },
            'digital_human': {
                'enabled': False,
                'heygen_api_key': ''
            },
            'storage': {
                'oss': {
                    'access_key_id': '',
                    'access_key_secret': '',
                    'bucket_name': '',
                    'endpoint': ''
                }
            },
            'local_materials': {
                'path': './local_materials',
                'vector_db_path': './chroma_db'
            }
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        self.config.update(new_config)
        self.save_config()
    
    def get(self, key: str, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value

# 全局配置实例
config = Config()
