import pytest
from services.embedding import EmbeddingService
import numpy as np

def test_embedding_service_initialization():
    service = EmbeddingService(model_name="all-MiniLM-L6-v2")
    assert service.model_name == "all-MiniLM-L6-v2"
    # Model is not loaded until accessed
    assert service._model is None

def test_embedding_service_generate_embeddings():
    service = EmbeddingService(model_name="all-MiniLM-L6-v2")
    texts = ["hello world", "this is a test"]
    
    embeddings = service.generate_embeddings(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
    assert isinstance(embeddings[0][0], float)

def test_embedding_service_generate_embedding():
    service = EmbeddingService(model_name="all-MiniLM-L6-v2")
    text = "hello world"
    
    embedding = service.generate_embedding(text)
    
    assert len(embedding) == 384
    assert isinstance(embedding[0], float)

def test_embedding_service_compute_similarities():
    service = EmbeddingService()
    
    # Use dummy vectors
    query = [1.0, 0.0, 0.0]
    chunks = [
        [1.0, 0.0, 0.0],  # Exact match (sim 1.0)
        [0.0, 1.0, 0.0],  # Orthogonal (sim 0.0)
        [-1.0, 0.0, 0.0], # Opposite (sim -1.0)
        [0.5, 0.5, 0.0],  # Some similarity
    ]
    
    similarities = service.compute_similarities(query, chunks)
    
    assert len(similarities) == 4
    assert similarities[0] == pytest.approx(1.0)
    assert similarities[1] == pytest.approx(0.0)
    assert similarities[2] == pytest.approx(-1.0)
    assert similarities[3] > 0.0 and similarities[3] < 1.0
