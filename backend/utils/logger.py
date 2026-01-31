"""
日志系统
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    设置日志器
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径
        level: 日志级别
    
    Returns:
        配置好的日志器
    """
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 创建默认日志器
default_logger = setup_logger(
    'auto_video_agent',
    f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
)
