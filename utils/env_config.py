from dotenv import dotenv_values,set_key


def get_env_config():
    value = dotenv_values()
    for k,v in value.items():
        value[k] = mask_range(v,1,len(v)-2)
    return value

def set_env_value(key: str, value: str):
    set_key('.env', key, value)
    
def mask_range(text, start, end):
    if start == -1 or end == -1 or start > end:
        return text  # 没找到就返回原文

    # 替换中间部分为 *
    masked = text[:start] + "*" * (end - start + 1) + text[end+1:]
    return masked