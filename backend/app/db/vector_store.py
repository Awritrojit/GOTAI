import chromadb
from sentence_transformers import SentenceTransformer
from .data_models import Node
from .. import config
from typing import Optional, List
import logging
import os

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        # Ensure the database directory exists and has proper permissions
        os.makedirs(config.VECTOR_DB_PATH, exist_ok=True)
        
        # Use absolute path to avoid any relative path issues
        db_path = os.path.abspath(config.VECTOR_DB_PATH)
        
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast, local
        self.collection = self.client.get_or_create_collection(name=config.COLLECTION_NAME)
        
        logger.info(f"Vector store initialized with database at: {db_path}")

    def clear_collection(self):
        """Clear all data from the collection"""
        try:
            # Delete the collection if it exists
            try:
                self.client.delete_collection(name=config.COLLECTION_NAME)
                logger.info("Deleted existing collection")
            except ValueError:
                # Collection doesn't exist, which is fine
                logger.info("Collection didn't exist, nothing to delete")
            
            # Create a fresh collection
            self.collection = self.client.get_or_create_collection(name=config.COLLECTION_NAME)
            logger.info("Collection cleared and recreated successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def add_node(self, node: Node):
        """Add a node to the vector store"""
        try:
            embedding = self.embedding_model.encode(node.text).tolist()
            node.embedding = embedding
            
            # Prepare metadata (exclude embedding from metadata and filter None values)
            metadata = node.dict(exclude={'embedding'})
            # Remove None values as ChromaDB doesn't accept them
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Check if node already exists
            try:
                existing = self.collection.get(ids=[node.id])
                if existing['ids']:
                    # Node exists, update it
                    self.collection.upsert(
                        ids=[node.id],
                        embeddings=[embedding],
                        metadatas=[metadata]
                    )
                    logger.info(f"Updated existing node {node.id} in vector store")
                else:
                    # Node doesn't exist, add it
                    self.collection.add(
                        ids=[node.id],
                        embeddings=[embedding],
                        metadatas=[metadata]
                    )
                    logger.info(f"Added new node {node.id} to vector store")
            except Exception:
                # If get() fails, assume node doesn't exist and try add()
                self.collection.add(
                    ids=[node.id],
                    embeddings=[embedding],
                    metadatas=[metadata]
                )
                logger.info(f"Added node {node.id} to vector store")
        except Exception as e:
            logger.error(f"Error adding node to vector store: {e}")
            raise

    def get_all_nodes_for_graph(self) -> List[Node]:
        """Retrieve all nodes for visualization"""
        try:
            nodes_data = self.collection.get(include=["metadatas"])
            nodes = []
            for meta in nodes_data['metadatas']:
                # Ensure parent_id is set to None if missing
                if 'parent_id' not in meta:
                    meta['parent_id'] = None
                nodes.append(Node(**meta))
            return nodes
        except Exception as e:
            logger.error(f"Error retrieving nodes: {e}")
            return []

    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """Get a specific node by ID"""
        try:
            data = self.collection.get(ids=[node_id], include=["metadatas"])
            if data['metadatas']:
                meta = data['metadatas'][0]
                # Ensure parent_id is set to None if missing
                if 'parent_id' not in meta:
                    meta['parent_id'] = None
                return Node(**meta)
            return None
        except Exception as e:
            logger.error(f"Error getting node by ID: {e}")
            return None

    def find_relevant_knowledge(self, query_text: str, n_results: int = 3) -> str:
        """Find relevant knowledge for providing context to agents"""
        try:
            query_embedding = self.embedding_model.encode(query_text).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding], 
                n_results=n_results
            )
            if results['metadatas'] and results['metadatas'][0]:
                return "\n".join([meta['text'] for meta in results['metadatas'][0]])
            return ""
        except Exception as e:
            logger.error(f"Error finding relevant knowledge: {e}")
            return ""

# Global instance
vector_store_client = VectorStore()

def reset_vector_store():
    """Create a new vector store instance and replace the global one"""
    global vector_store_client
    vector_store_client = VectorStore()
    return vector_store_client
