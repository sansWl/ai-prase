from pydantic import BaseModel
from typing import Optional



class UserInfoRequest(BaseModel):
    """用户信息请求模型"""
    userId: Optional[str] = None
    username: str
    password: str
    rememberMe: Optional[bool] = False
    email: Optional[str] = None
    salt: Optional[str] = None
    token: Optional[str] = None
