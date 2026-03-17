import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from utils import logger

load_dotenv()



class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI')
        self.user = os.getenv('NEO4J_USER')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.database = os.getenv('NEO4J_DATABASE', 'neo4j')
        self.graph = None
        self.connect()
    
    def connect(self):
        try:
            self.graph = Neo4jGraph(
                url=self.uri,
                username=self.user,
                password=self.password,
                database=self.database
            )
            logger.info(f"Successfully connected to Neo4j database '{self.database}'")
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j: {e}")
            self.graph = None
    
    def close(self):
        if self.graph:
            self.graph = None
    
    def execute_query(self, query, parameters=None):
        if not self.graph:
            logger.warning("Not connected to Neo4j, returning empty result")
            return []
        
        try:
            result = self.graph.query(query, parameters or {})
            return result
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return []
    
    def execute_write(self, query, parameters=None):
        if not self.graph:
            logger.warning("Not connected to Neo4j, skipping write operation")
            return []
        
        try:
            result = self.graph.query(query, parameters or {})
            return result
        except Exception as e:
            logger.error(f"Neo4j write error: {e}")
            return []
    
    def add_document(self, text, metadata=None):
        if not self.graph:
            logger.warning("Not connected to Neo4j, skipping document addition")
            return []
        
        try:
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
        except Exception as e:
            logger.error(f"Neo4j add document error: {e}")
            return []
