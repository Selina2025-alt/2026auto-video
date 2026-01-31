"""
用户数据库（简化版，使用JSON文件存储）
生产环境应使用真实数据库如PostgreSQL/MySQL
"""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from .models import User

class UserDatabase:
    """用户数据库"""
    
    def __init__(self, db_file: str = "users_db.json"):
        self.db_file = db_file
        self.users: Dict[str, Dict[str, Any]] = {}
        self.load()
    
    def load(self):
        """从文件加载数据"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
    
    def save(self):
        """保存数据到文件"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def create_user(self, email: str, username: str, password: str) -> User:
        """创建用户"""
        # 检查邮箱是否已存在
        if self.get_user_by_email(email):
            raise ValueError("邮箱已被注册")
        
        user_id = str(uuid.uuid4())
        password_hash = User.hash_password(password)
        
        user_data = {
            'user_id': user_id,
            'email': email,
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'config': {}
        }
        
        self.users[user_id] = user_data
        self.save()
        
        return self._dict_to_user(user_data)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        for user_data in self.users.values():
            if user_data['email'] == email:
                return self._dict_to_user(user_data)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """通过ID获取用户"""
        user_data = self.users.get(user_id)
        if user_data:
            return self._dict_to_user(user_data)
        return None
    
    def update_last_login(self, user_id: str):
        """更新最后登录时间"""
        if user_id in self.users:
            self.users[user_id]['last_login'] = datetime.now().isoformat()
            self.save()
    
    def update_user_config(self, user_id: str, config_key: str, config_value: Any):
        """更新用户配置"""
        if user_id in self.users:
            if 'config' not in self.users[user_id]:
                self.users[user_id]['config'] = {}
            self.users[user_id]['config'][config_key] = config_value
            self.save()
    
    def get_user_config(self, user_id: str, config_key: str) -> Optional[Any]:
        """获取用户配置"""
        if user_id in self.users:
            return self.users[user_id].get('config', {}).get(config_key)
        return None
    
    def _dict_to_user(self, user_data: Dict[str, Any]) -> User:
        """字典转User对象"""
        return User(
            user_id=user_data['user_id'],
            email=user_data['email'],
            username=user_data['username'],
            password_hash=user_data['password_hash'],
            created_at=datetime.fromisoformat(user_data['created_at']) if user_data.get('created_at') else None,
            last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None,
            config=user_data.get('config', {})
        )

# 全局数据库实例
user_db = UserDatabase()
