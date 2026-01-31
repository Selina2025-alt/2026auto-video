"""
用户数据模型
"""
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import secrets

class User:
    """用户模型"""
    
    def __init__(
        self,
        user_id: str,
        email: str,
        username: str,
        password_hash: str,
        created_at: datetime = None,
        last_login: datetime = None,
        config: Dict[str, Any] = None
    ):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
        self.config = config or {}
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            salt, pwd_hash = password_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == pwd_hash
        except:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
