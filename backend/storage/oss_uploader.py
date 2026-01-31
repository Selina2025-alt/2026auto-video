"""
OSS文件上传器
支持阿里云OSS文件上传
"""
import os
import oss2
from typing import Optional, Dict, Any
from datetime import datetime


class OSSUploader:
    """阿里云OSS文件上传器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化OSS上传器

        Args:
            config: {
                'access_key_id': OSS访问密钥ID,
                'access_key_secret': OSS访问密钥Secret,
                'bucket_name': 存储桶名称,
                'endpoint': OSS端点
            }
        """
        self.access_key_id = config.get('access_key_id', '')
        self.access_key_secret = config.get('access_key_secret', '')
        self.bucket_name = config.get('bucket_name', '')
        self.endpoint = config.get('endpoint', '')

        self.auth = None
        self.bucket = None

        # 如果配置完整，创建认证
        if self.is_configured():
            self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(
            self.access_key_id and
            self.access_key_secret and
            self.bucket_name and
            self.endpoint
        )

    def upload_video(
        self,
        video_path: str,
        record_id: str,
        folder: str = "videos"
    ) -> Optional[str]:
        """
        上传视频到OSS

        Args:
            video_path: 本地视频文件路径
            record_id: 记录ID（用于生成文件名）
            folder: OSS存储文件夹

        Returns:
            OSS文件URL，失败返回None
        """
        if not self.is_configured():
            print("OSS未配置，无法上传")
            return None

        if not os.path.exists(video_path):
            print(f"视频文件不存在: {video_path}")
            return None

        try:
            # 生成OSS文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{record_id}_{timestamp}.mp4"
            object_key = f"{folder}/{filename}"

            # 上传文件
            with open(video_path, 'rb') as file:
                result = self.bucket.put_object(object_key, file)

            if result.status == 200:
                # 构建访问URL
                # 如果是公共读桶，直接返回URL
                url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '').replace('http://', '')}/{object_key}"
                print(f"视频上传成功: {url}")
                return url
            else:
                print(f"视频上传失败，状态码: {result.status}")
                return None

        except Exception as e:
            print(f"视频上传异常: {str(e)}")
            return None

    def upload_file(
        self,
        file_path: str,
        object_key: str,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        上传任意文件到OSS

        Args:
            file_path: 本地文件路径
            object_key: OSS对象键
            headers: 可选的HTTP头

        Returns:
            是否上传成功
        """
        if not self.is_configured():
            print("OSS未配置，无法上传")
            return False

        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return False

        try:
            with open(file_path, 'rb') as file:
                result = self.bucket.put_object(object_key, file, headers=headers)

            return result.status == 200

        except Exception as e:
            print(f"文件上传异常: {str(e)}")
            return False

    def delete_file(self, object_key: str) -> bool:
        """
        删除OSS文件

        Args:
            object_key: OSS对象键

        Returns:
            是否删除成功
        """
        if not self.is_configured():
            print("OSS未配置")
            return False

        try:
            result = self.bucket.delete_object(object_key)
            return result.status == 200

        except Exception as e:
            print(f"文件删除异常: {str(e)}")
            return False

    def file_exists(self, object_key: str) -> bool:
        """
        检查OSS文件是否存在

        Args:
            object_key: OSS对象键

        Returns:
            文件是否存在
        """
        if not self.is_configured():
            return False

        try:
            return self.bucket.object_exists(object_key)
        except Exception:
            return False

    def get_file_url(self, object_key: str, expires: int = 3600) -> Optional[str]:
        """
        获取OSS文件的签名URL

        Args:
            object_key: OSS对象键
            expires: URL过期时间（秒）

        Returns:
            签名URL
        """
        if not self.is_configured():
            return None

        try:
            url = self.bucket.sign_url('GET', object_key, expires)
            return url
        except Exception as e:
            print(f"生成URL异常: {str(e)}")
            return None


# 测试代码
if __name__ == "__main__":
    # 测试配置
    config = {
        'access_key_id': 'your_access_key_id',
        'access_key_secret': 'your_access_key_secret',
        'bucket_name': 'your_bucket_name',
        'endpoint': 'oss-cn-hangzhou.aliyuncs.com'
    }

    uploader = OSSUploader(config)

    if uploader.is_configured():
        print("OSS配置成功")
        # 测试上传
        # url = uploader.upload_video('./test.mp4', 'test_record_id')
        # print(f"上传URL: {url}")
    else:
        print("OSS配置不完整")
