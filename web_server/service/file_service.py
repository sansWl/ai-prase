import io
from utils.file_convert import convert_file_to_md
from info.analyze_strategy import getTextchunk_info
from utils import logger,neo4jUtils


async def get_textchunk_info(content: bytes)->dict:
    """获取文本块信息"""
    info_chunks = getTextchunk_info(convert_file_to_md(io.BytesIO(content)))
    return info_chunks