import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service responsible for generating semantic embeddings using sentence-transformers.
    
    The model is loaded once upon initialization and reused for efficiency.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        
    @property
    def model(self):
        # Lazy load to avoid slowing down startup if embeddings aren't used
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def generate_embedding(self, text: str) -> List[float]:
        """Generates an embedding for a single text string."""
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text strings.
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            List of embedding vectors (list of floats).
        """
        if not texts:
            return []
            
        # The encode method returns a numpy array, which we convert to a list of lists of floats
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def compute_similarities(self, query_embedding: List[float], chunk_embeddings: List[List[float]]) -> List[float]:
        """Computes cosine similarity between a query embedding and a list of chunk embeddings.
        
        Args:
            query_embedding: The embedding of the search query.
            chunk_embeddings: List of embeddings for the chunks.
            
        Returns:
            List of cosine similarity scores (-1 to 1).
        """
        if not chunk_embeddings:
            return []
            
        q_vec = np.array(query_embedding)
        c_vecs = np.array(chunk_embeddings)
        
        # Calculate cosine similarity: (A dot B) / (||A|| ||B||)
        # Using numpy dot and norm
        dot_products = np.dot(c_vecs, q_vec)
        
        q_norm = np.linalg.norm(q_vec)
        c_norms = np.linalg.norm(c_vecs, axis=1)
        
        # Avoid division by zero
        norms = q_norm * c_norms
        norms[norms == 0] = 1e-10
        
        similarities = dot_products / norms
        
        return similarities.tolist()
