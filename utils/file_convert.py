from markitdown import MarkItDown
import os

md = MarkItDown()

def useLLMs_convert():
    # md._llm_client=LLMsFactory().create_llm()
    pass
    
def convert_file_to_text(file_path):
    """将文件转换为文本格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        转换后的文本内容
    """
    markdown = md.convert(file_path)
    return markdown.text_content    

def convert_file_to_md(file_path):
    """将文件转换为 Markdown 格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        转换后的 Markdown 内容
    """
    markdown = md.convert(file_path)
    return markdown.markdown
