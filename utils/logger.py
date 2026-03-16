import os
import logging
import traceback
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    """日志工具类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志配置"""
        # 日志目录（默认为项目当前路径）
        log_dir = os.getcwd()
        log_file = os.path.join(log_dir, 'app.log')
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志记录器
        self.logger = logging.getLogger('AI-Prase')
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            
            # 文件处理器（带轮转）
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            
            # 添加处理器
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
        
        self.logger.info(f"日志初始化完成，日志文件: {log_file}")
    
    def debug(self, message: str, *args, **kwargs):
        """调试级别的日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """信息级别的日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告级别的日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """错误级别的日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """严重级别的日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """异常级别的日志，会自动记录异常信息"""
        self.logger.exception(message, *args, **kwargs)
    
    def log(self, level: int, message: str, *args, **kwargs):
        """自定义级别的日志"""
        self.logger.log(level, message, *args, **kwargs)


# 全局日志实例
logger = Logger()


def get_logger() -> Logger:
    """获取日志实例"""
    return logger


# 便捷函数
def debug(message: str, *args, **kwargs):
    """调试级别的日志"""
    logger.debug(message, *args, **kwargs)

def info(message: str, *args, **kwargs):
    """信息级别的日志"""
    logger.info(message, *args, **kwargs)

def warning(message: str, *args, **kwargs):
    """警告级别的日志"""
    logger.warning(message, *args, **kwargs)

def error(message: str, *args, **kwargs):
    """错误级别的日志"""
    logger.error(message, *args, **kwargs)

def critical(message: str, *args, **kwargs):
    """严重级别的日志"""
    logger.critical(message, *args, **kwargs)

def exception(message: str, *args, **kwargs):
    """异常级别的日志"""
    logger.exception(message, *args, **kwargs)
