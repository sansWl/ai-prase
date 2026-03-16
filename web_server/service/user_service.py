from utils import logger,neo4jUtils,crypto_utils,redisUtils
from web_server.class_model import user

def user_register(user: user.UserInfoRequest)->user.UserInfoRequest or None:
    """用户注册"""
      # 密码加密
    encrypted_password = crypto_utils.hash_password(user.password,crypto_utils.generate_random_salt())
    user.password = encrypted_password[0]
    user.salt = encrypted_password[1]

    user_node = neo4jUtils.get_node("User",{"username":user.username})
    if user_node:
        logger.error("用户已存在")
        return None

    neo4jUtils.create_node("User",{
        "username": user.username,
        "userId": user.salt,
        "email": user.email,
        "password": user.password,
        "salt": user.salt
    })
    user.userId = user.salt
    return user


def user_login(user: user.UserInfoRequest)->user.UserInfoRequest or None:
    """用户登录"""
    user_node = neo4jUtils.get_node("User",{"username":user.username})
    if not user_node:
        logger.error("用户不存在")
        return None
    user_node = crypto_utils.verify_password(user.password,user_node[0]['n']["password"],user_node[0]['n']["salt"])    
    if not user_node:
        logger.error("密码错误")
        return None

    user.token = "Bearer_" + crypto_utils.generate_random_string() 
    ttl = 60 * 5;
    if user.rememberMe:
        ttl =  60*60*24*7  
    redisUtils.set_redis_key(user.token, user.model_dump_json(), ttl)    
    return user


def get_user_remember_me(token: str)-> user.UserInfoRequest or None:
    """根据token获取用户信息"""
    user = redisUtils.get_redis_key(token)
    if not user:
        logger.error("用户不存在")
        return None
    return user