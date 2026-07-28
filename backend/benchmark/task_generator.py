import asyncio
import os
import json
import httpx
from pydantic import BaseModel
from .config import DATASET_DIR, API_BASE_URL, TASKS_PER_DOCUMENT
from api.dependencies import get_llm_service

class TaskSchema(BaseModel):
    title: str
    description: str
    expected_output: str
    ground_truth: str
    rubric: str
    difficulty: str
    department: str

async def generate_tasks_for_document(llm_service, doc_name: str, content: str) -> list[dict]:
    prompt = f"""
    Based on the following document, generate {TASKS_PER_DOCUMENT} benchmark tasks.
    The tasks should exercise information retrieval and reasoning based on the document's content.
    For each task, provide the following fields in a JSON array format (no markdown code blocks, just raw JSON):
    - title: short title for the task
    - description: user query or instruction
    - expected_output: what the AI should output
    - ground_truth: factual information extracted from the document
    - rubric: instructions on how an LLM Judge should evaluate the AI's answer
    - difficulty: Easy, Medium, or Hard
    - department: Relevant department (e.g., HR, IT, Legal, General)

    Document Content:
    {content[:15000]}  # limit content to avoid context limits if very large
    """

    print(f"Requesting tasks for {doc_name} from LLM provider...")
    result = await llm_service.generate_raw(prompt)
    print(f"Generated tasks for {doc_name} using {result.get('provider')} ({result.get('model')}) in {result.get('latency_ms')}ms")
    
    # Simple JSON extraction
    text = result["text"].strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
        
    try:
        tasks = json.loads(text.strip())
        return tasks
    except Exception as e:
        print(f"Failed to parse tasks for {doc_name}: {e}")
        return []

async def upload_task(client: httpx.AsyncClient, world_id: str, document_id: str, task_data: dict) -> dict:
    def to_str(val):
        if isinstance(val, list):
            return "\n".join(str(v) for v in val)
        return str(val) if val is not None else ""

    payload = {
        "world_id": world_id,
        "document_id": document_id,
        "title": to_str(task_data.get("title", "Untitled Task"))[:512],
        "description": to_str(task_data.get("description", "")),
        "expected_output": to_str(task_data.get("expected_output", "")),
        "ground_truth": to_str(task_data.get("ground_truth", "")),
        "rubric": to_str(task_data.get("rubric", "")),
        "difficulty": to_str(task_data.get("difficulty", "Medium"))[:50],
        "department": to_str(task_data.get("department", "General"))[:100]
    }
    
    response = await client.post(
        f"{API_BASE_URL}/tasks",
        json=payload
    )
    if response.status_code >= 400:
        print(f"Failed to upload task. Response: {response.text}")
    response.raise_for_status()
    return response.json()

async def generate_and_upload_tasks(world_id: str, uploaded_docs: list[dict]) -> list[dict]:
    llm_service = get_llm_service()
    
    md_files = list(DATASET_DIR.glob("*.md"))
    
    # Create a mapping from filename to document_id for the uploaded documents
    doc_id_map = {doc["filename"]: doc["id"] for doc in uploaded_docs}
    
    all_generated_tasks = []
    
    for file in md_files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        doc_id = doc_id_map.get(file.name)
        if not doc_id:
            print(f"Warning: {file.name} not found in uploaded docs. Skipping task generation.")
            continue
            
        print(f"Generating tasks for {file.name}...")
        tasks = await generate_tasks_for_document(llm_service, file.name, content)
        
        # Attach the document_id to each task so we can upload it correctly
        for t in tasks:
            t["_document_id"] = doc_id
            
        all_generated_tasks.extend(tasks)
        await asyncio.sleep(5)  # Rate limit avoidance

    uploaded_tasks = []
    async with httpx.AsyncClient(timeout=300.0) as client:
        for t in all_generated_tasks:
            try:
                doc_id = t.pop("_document_id")
                task_obj = await upload_task(client, world_id, doc_id, t)
                uploaded_tasks.append(task_obj)
            except Exception as e:
                title_str = str(t.get('title')).encode('ascii', 'replace').decode('ascii')
                print(f"Error uploading task {title_str}: {e}")
                
    print(f"Uploaded {len(uploaded_tasks)} tasks successfully.")
    return uploaded_tasks
