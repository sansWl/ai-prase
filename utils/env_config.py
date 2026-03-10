from dotenv import dotenv_values,set_key


def get_env_config():
    return dotenv_values()

def set_env_value(key: str, value: str):
    set_key('.env', key, value)
    
