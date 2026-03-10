from dotenv import load_dotenv
from utils.similarity import cosine_similarity, calculate_similarity_batch, embeddings_model, get_top_similar

load_dotenv()

# 全局 Embedding 实例
embedding_instance = None


def get_instance():
    """获取全局 Embedding 实例"""
    global embedding_instance
    if embedding_instance is None:
        embedding_instance = EmbeddingTool()
    return embedding_instance


class EmbeddingTool:
    def __init__(self):
        self.embedding_model= embeddings_model
        
    def embed_text(self, text: str, embedding_type: str = None):
        """对单个文本进行 embedding"""
        return self.embedding_model.embed_query(text)
    
    def embed_documents(self, documents: list, embedding_type: str = None):
        """对多个文档进行 embedding"""
        return self.embedding_model.embed_documents([doc.page_content if hasattr(doc, 'page_content') else doc for doc in documents])
    
    def get_embedding_dimension(self, embedding_type: str = None):
        """获取 embedding 维度"""
        # 嵌入一个测试文本以获取维度
        test_embedding = self.embed_text("test", embedding_type)
        return len(test_embedding)
    
    def calculate_similarity(self, text1: str, text2: str, embedded: bool = True):
        """计算两个文本之间的相似度"""
        return cosine_similarity(text1, text2, embedded)
    
    def calculate_similarity_batch(self, query: str, documents: list, embedding_type: str = None):
        """计算查询文本与多个文档之间的相似度"""
        return calculate_similarity_batch(query, documents)
    
    def get_top_similar_documents(self, query: str, documents: list, top_k: int = 5, embedding_type: str = None):
        """获取与查询文本最相似的文档"""
        similarities = self.calculate_similarity_batch(query, documents, embedding_type)
        return get_top_similar(documents, similarities, top_k)
