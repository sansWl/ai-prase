import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jVector
from factories.llmsFactory.llms_factory import LLMsFactory
from factories.embeddingFactory.embedding_factory import EmbeddingFactory

load_dotenv()

# 全局RAG系统实例
rag_system_instance = None


def get_rag_system():
    """获取全局RAG系统实例"""
    global rag_system_instance
    if rag_system_instance is None:
        rag_system_instance = RAGSystem()
    return rag_system_instance


class RAGSystem:
    def __init__(self):
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_user = os.getenv('NEO4J_USER')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        self.llm_factory = LLMsFactory()
        self.embedding_factory = EmbeddingFactory()
        
        self.llm = None
        self.embeddings = None
        self.vector_store = None
    
    def initialize(self, llm_type: str = None, embedding_type: str = None):
        self.llm = self.llm_factory.create_llm(llm_type)
        self.embeddings = self.embedding_factory.create_embedding(embedding_type)
        
        try:
            self.vector_store = Neo4jVector.from_existing_index(
                embedding=self.embeddings,
                url=self.neo4j_uri,
                username=self.neo4j_user,
                password=self.neo4j_password,
                index_name="vector_index",
                node_label="Document",
                text_node_property="text",
                embedding_node_property="embedding"
            )
        except Exception as e:
            print(f"Warning: Could not load existing index, creating new one: {e}")
            self.vector_store = Neo4jVector.from_documents(
                documents=[],
                embedding=self.embeddings,
                url=self.neo4j_uri,
                username=self.neo4j_user,
                password=self.neo4j_password,
                index_name="vector_index",
                node_label="Document",
                text_node_property="text",
                embedding_node_property="embedding"
            )
    
    def add_documents(self, documents):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call initialize() first.")
        
        self.vector_store.add_documents(documents)
        return {"status": "success", "message": f"Added {len(documents)} documents"}
    
    def similarity_search(self, query: str, k: int = 5):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call initialize() first.")
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 5):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call initialize() first.")
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def generate_response(self, query: str, k: int = 5):
        if not self.vector_store or not self.llm:
            raise ValueError("System not initialized. Call initialize() first.")
        
        relevant_docs = self.similarity_search(query, k=k)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        response = self.llm.invoke(prompt)
        return {
            "answer": response.content if hasattr(response, 'content') else str(response),
            "sources": [doc.metadata for doc in relevant_docs]
        }
