import asyncio
import httpx
from .config import API_BASE_URL, DEFAULT_MODELS, CONCURRENCY

async def get_prompt_templates(client: httpx.AsyncClient) -> list[dict]:
    res = await client.get(f"{API_BASE_URL}/prompt-templates")
    if res.status_code == 200:
        return res.json()
    return []

async def launch_experiment(client: httpx.AsyncClient, task_id: str, models: list[str], prompt_template_id: str = None) -> dict:
    payload = {
        "name": f"Benchmark Exp {task_id[:8]}",
        "description": "Automated Benchmark Experiment",
        "task_id": task_id,
        "models": models
    }
    if prompt_template_id:
        payload["prompt_template_id"] = prompt_template_id

    res = await client.post(f"{API_BASE_URL}/experiments", json=payload)
    if res.status_code == 201:
        return res.json()
    print(f"Error launching experiment for task {task_id}: {res.text}")
    return None

async def run_experiments(tasks: list[dict]) -> list[str]:
    print("Launching experiments...")
    experiment_ids = []
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Get available templates
        templates = await get_prompt_templates(client)
        # Use at most 2 templates for benchmarking to avoid explosion of runs if there are many
        templates_to_use = templates[:2] if templates else [None]
        
        semaphore = asyncio.Semaphore(CONCURRENCY)
        
        async def _launch(task_id, template_id):
            async with semaphore:
                exp = await launch_experiment(client, task_id, DEFAULT_MODELS, template_id)
                if exp:
                    experiment_ids.append(exp["id"])
                    
        launch_tasks = []
        for t in tasks:
            for template in templates_to_use:
                template_id = template["id"] if template else None
                launch_tasks.append(_launch(t["id"], template_id))
                
        await asyncio.gather(*launch_tasks)
        
    print(f"Launched {len(experiment_ids)} experiments.")
    return experiment_ids
