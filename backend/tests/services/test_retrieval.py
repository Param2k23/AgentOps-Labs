import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.exceptions import NotFoundException, BadRequestException
from models.document import Document
from models.document_chunk import DocumentChunk
from models.task import Task
from services.retrieval import RetrievalService

@pytest.fixture
def mock_document_repository():
    return AsyncMock()

@pytest.fixture
def mock_document_chunk_repository():
    return AsyncMock()

@pytest.fixture
def mock_task_repository():
    return AsyncMock()

@pytest.fixture
def retrieval_service(mock_document_repository, mock_document_chunk_repository, mock_task_repository):
    return RetrievalService(
        document_repository=mock_document_repository,
        document_chunk_repository=mock_document_chunk_repository,
        task_repository=mock_task_repository,
    )

@pytest.mark.asyncio
async def test_chunk_document_success(retrieval_service, mock_document_repository, mock_document_chunk_repository):
    document_id = uuid.uuid4()
    mock_doc = Document(id=document_id, extracted_text="This is a test document with some text to chunk.")
    mock_document_repository.get.return_value = mock_doc
    
    # Mock create to just return the passed object for testing purposes
    async def mock_create(**kwargs):
        return DocumentChunk(**kwargs)
        
    mock_document_chunk_repository.create = AsyncMock(side_effect=mock_create)

    chunks = await retrieval_service.chunk_document(document_id, chunk_size=10)
    
    assert len(chunks) == 5
    mock_document_chunk_repository.delete_by_document.assert_called_once_with(document_id)
    assert mock_document_chunk_repository.create.call_count == 5
    assert chunks[0].text == "This is a "

@pytest.mark.asyncio
async def test_chunk_document_missing_doc(retrieval_service, mock_document_repository):
    mock_document_repository.get.return_value = None
    with pytest.raises(NotFoundException):
        await retrieval_service.chunk_document(uuid.uuid4())

@pytest.mark.asyncio
async def test_chunk_document_no_text(retrieval_service, mock_document_repository):
    mock_doc = Document(id=uuid.uuid4(), extracted_text=None)
    mock_document_repository.get.return_value = mock_doc
    with pytest.raises(BadRequestException):
        await retrieval_service.chunk_document(mock_doc.id)

@pytest.mark.asyncio
async def test_retrieve_chunks_success(retrieval_service, mock_task_repository, mock_document_chunk_repository):
    task_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    mock_task = Task(id=task_id, document_id=doc_id, title="Test", description="apple banana")
    mock_task_repository.get.return_value = mock_task
    
    chunk1 = DocumentChunk(text="apple is good", chunk_index=0)
    chunk2 = DocumentChunk(text="banana is yellow", chunk_index=1)
    chunk3 = DocumentChunk(text="apple and banana are fruits", chunk_index=2)
    chunk4 = DocumentChunk(text="unrelated text", chunk_index=3)
    
    mock_document_chunk_repository.get_by_document.return_value = [chunk1, chunk2, chunk3, chunk4]
    
    results = await retrieval_service.retrieve_chunks(task_id, top_k=2)
    
    assert len(results) == 2
    # chunk3 has both apple and banana, so it should be first
    assert results[0]["chunk"].chunk_index == 2
    # chunk1 and chunk2 each have 1 overlap, tie breaker is length. chunk2 is 16 chars, chunk1 is 13 chars
    assert results[1]["chunk"].chunk_index == 1

@pytest.mark.asyncio
async def test_retrieve_chunks_missing_task(retrieval_service, mock_task_repository):
    mock_task_repository.get.return_value = None
    with pytest.raises(NotFoundException):
        await retrieval_service.retrieve_chunks(uuid.uuid4())

@pytest.mark.asyncio
async def test_retrieve_chunks_no_document(retrieval_service, mock_task_repository):
    mock_task = Task(id=uuid.uuid4(), document_id=None)
    mock_task_repository.get.return_value = mock_task
    with pytest.raises(BadRequestException):
        await retrieval_service.retrieve_chunks(mock_task.id)
