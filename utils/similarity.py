import numpy as np
from factories.embeddingFactory.embedding_factory import EmbeddingFactory
from scipy.spatial.distance import cosine


global embeddings_model 
embeddings_model = EmbeddingFactory().create_embedding()


def cosine_similarity(vec1, vec2,embedded:bool=True):
    """计算两个向量的余弦相似度
    
    Args:
        vec1: 第一个向量
        vec2: 第二个向量
    
    Returns:
        余弦相似度值（范围：-1 到 1，值越大表示相似度越高）
    """
    if not embedded:
        vec1, vec2 = embeddings_model.embed_documents([vec1, vec2])
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same length")
    
    # 使用 scipy 的 cosine 函数，它返回的是距离，所以需要转换为相似度
    return 1 - cosine(vec1, vec2)


def calculate_similarity_batch(query_embedding, document_embeddings):
    f"""批量计算查询向量与多个文档向量的相似度
    
    Args:
        query_embedding: 查询向量
        document_embeddings: 文档向量列表
    
    Returns:
        相似度值列表
        {{
            document: 文档
            similarity: 余弦相似度值
        }}
    """
    similarities = []
    query_vector = embeddings_model.embed_query(query_embedding)
    document_vectors = embeddings_model.embed_documents(document_embeddings)
    for (doc_embedding,doc_vector) in zip(document_embeddings,document_vectors):
        similarity = cosine_similarity(query_vector, doc_vector)
        similarities.append({"document":doc_embedding,"similarity":similarity})
    return similarities


def get_top_similar(documents, similarities, top_k=5):
    """获取相似度最高的前 k 个文档
    
    Args:
        documents: 文档列表
        similarities: 相似度值列表
        top_k: 返回的文档数量
    
    Returns:
        排序后的文档和相似度列表
    """
    # 按相似度排序
    sorted_pairs = sorted(zip(documents, similarities), key=lambda x: x[1], reverse=True)
    # 返回前 top_k 个
    return sorted_pairs[:top_k]
