import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()


class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI')
        self.user = os.getenv('NEO4J_USER')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.graph = None
        self.connect()
    
    def connect(self):
        try:
            self.graph = Neo4jGraph(
                url=self.uri,
                username=self.user,
                password=self.password
            )
        except Exception as e:
            print(f"Warning: Could not connect to Neo4j: {e}")
            self.graph = None
    
    def close(self):
        if self.graph:
            self.graph = None
    
    def execute_query(self, query, parameters=None):
        if not self.graph:
            raise ValueError("Not connected to Neo4j")
        
        result = self.graph.query(query, parameters or {})
        return result
    
    def execute_write(self, query, parameters=None):
        if not self.graph:
            raise ValueError("Not connected to Neo4j")
        
        result = self.graph.query(query, parameters or {})
        return result
    
    def add_document(self, text, metadata=None):
        if not self.graph:
            raise ValueError("Not connected to Neo4j")
        
        query = """
        CREATE (d:Document {
            text: $text,
            metadata: $metadata,
            created_at: datetime()
        })
        RETURN d
        """
        result = self.graph.query(query, {
            'text': text,
            'metadata': metadata or {}
        })
        return result
