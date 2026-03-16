import os
import base64
import hashlib
import hmac
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

load_dotenv()


class CryptoUtils:
    """加密工具类"""
    
    _instance = None
    _fernet = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cipher()
        return cls._instance
    
    def _init_cipher(self):
        """初始化加密器"""
        # 从环境变量获取密钥，如果没有则生成一个
        key = os.getenv('ENCRYPTION_KEY')
        if key:
            # 如果密钥是 base64 编码的字符串，直接使用
            try:
                self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
            except Exception:
                # 如果密钥格式不正确，从密码派生
                self._fernet = self._derive_key_from_password(key)
        else:
            # 生成新密钥（仅用于开发环境，生产环境应使用固定密钥）
            key = Fernet.generate_key()
            self._fernet = Fernet(key)
            print(f"⚠️  警告: 未设置 ENCRYPTION_KEY，已生成临时密钥: {key.decode()}")
            print("   请将上述密钥添加到 .env 文件的 ENCRYPTION_KEY 中")
    
    def _derive_key_from_password(self, password: str, salt: bytes = None) -> Fernet:
        """从密码派生加密密钥"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    # ==================== 对称加密 (Fernet) ====================
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        加密数据
        
        Args:
            data: 要加密的数据
        
        Returns:
            加密后的 base64 字符串
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self._fernet.encrypt(data)
        return encrypted.decode('utf-8')
    
    def decrypt(self, encrypted_data: Union[str, bytes]) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密的数据
        
        Returns:
            解密后的字符串
        """
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode('utf-8')
        
        decrypted = self._fernet.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        """加密字节数据"""
        return self._fernet.encrypt(data)
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """解密字节数据"""
        return self._fernet.decrypt(encrypted_data)
    
    # ==================== 哈希算法 ====================
    
    @staticmethod
    def md5(text: str) -> str:
        """MD5 哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha1(text: str) -> str:
        """SHA1 哈希"""
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha256(text: str) -> str:
        """SHA256 哈希"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha512(text: str) -> str:
        """SHA512 哈希"""
        return hashlib.sha512(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_file(file_path: str, algorithm: str = 'sha256') -> str:
        """
        计算文件哈希
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法 (md5, sha1, sha256, sha512)
        
        Returns:
            哈希值
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    # ==================== HMAC ====================
    
    @staticmethod
    def hmac_sha256(key: Union[str, bytes], message: Union[str, bytes]) -> str:
        """
        HMAC-SHA256
        
        Args:
            key: 密钥
            message: 消息
        
        Returns:
            HMAC 值
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        return hmac.new(key, message, hashlib.sha256).hexdigest()
    
    @staticmethod
    def hmac_sha512(key: Union[str, bytes], message: Union[str, bytes]) -> str:
        """HMAC-SHA512"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        return hmac.new(key, message, hashlib.sha512).hexdigest()
    
    # ==================== Base64 ====================
    
    @staticmethod
    def base64_encode(data: Union[str, bytes]) -> str:
        """Base64 编码"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def base64_decode(data: Union[str, bytes]) -> str:
        """Base64 解码"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64decode(data).decode('utf-8')
    
    @staticmethod
    def base64_url_encode(data: Union[str, bytes]) -> str:
        """Base64 URL 安全编码"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64encode(data).decode('utf-8')
    
    @staticmethod
    def base64_url_decode(data: Union[str, bytes]) -> str:
        """Base64 URL 安全解码"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64decode(data).decode('utf-8')
    
    # ==================== 密码学安全随机数 ====================
    
    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        """
        生成密码学安全的随机字符串
        
        Args:
            length: 字符串长度
        
        Returns:
            随机字符串
        """
        import secrets
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_random_bytes(length: int = 32) -> bytes:
        """生成密码学安全的随机字节"""
        import secrets
        return secrets.token_bytes(length)
    
    @staticmethod
    def generate_uuid() -> str:
        """生成 UUID"""
        import uuid
        return str(uuid.uuid4())
    
    # ==================== 密码哈希 (PBKDF2) ====================
    
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> tuple:
        """
        使用 PBKDF2 哈希密码
        
        Args:
            password: 密码
            salt: 盐值（可选）
        
        Returns:
            (哈希值, 盐值) 元组
        """
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        hashed = kdf.derive(password.encode('utf-8'))
        return base64.b64encode(hashed).decode('utf-8'), base64.b64encode(salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """
        验证密码
        
        Args:
            password: 待验证的密码
            hashed: 哈希值
            salt: 盐值
        
        Returns:
            是否匹配
        """
        try:
            salt_bytes = base64.b64decode(salt)
            new_hash, _ = CryptoUtils.hash_password(password, salt_bytes)
            return new_hash == hashed
        except Exception:
            return False
    
    # ==================== 实用工具 ====================
    
    @staticmethod
    def generate_encryption_key() -> str:
        """生成新的加密密钥"""
        return Fernet.generate_key().decode('utf-8')


# 全局加密工具实例
crypto_utils = CryptoUtils()


def get_crypto_utils() -> CryptoUtils:
    """获取加密工具实例"""
    return crypto_utils


# ==================== 便捷函数 ====================

def encrypt(data: Union[str, bytes]) -> str:
    """加密数据"""
    return crypto_utils.encrypt(data)


def decrypt(encrypted_data: Union[str, bytes]) -> str:
    """解密数据"""
    return crypto_utils.decrypt(encrypted_data)


def md5(text: str) -> str:
    """MD5 哈希"""
    return CryptoUtils.md5(text)


def sha256(text: str) -> str:
    """SHA256 哈希"""
    return CryptoUtils.sha256(text)


def base64_encode(data: Union[str, bytes]) -> str:
    """Base64 编码"""
    return CryptoUtils.base64_encode(data)


def base64_decode(data: Union[str, bytes]) -> str:
    """Base64 解码"""
    return CryptoUtils.base64_decode(data)


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    return CryptoUtils.generate_random_string(length)

def generate_random_salt(length: int = 32) -> str:
    """生成随机盐值"""
    return CryptoUtils.generate_random_bytes(length)

def hash_password(password: str, salt: bytes = None) -> tuple:
    """哈希密码"""
    return CryptoUtils.hash_password(password, salt)


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """验证密码"""
    return CryptoUtils.verify_password(password, hashed, salt)
