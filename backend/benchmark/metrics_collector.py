import asyncio
import time
import httpx
from .config import API_BASE_URL

async def wait_for_ingestion(client: httpx.AsyncClient, docs: list[dict], timeout: int = 300):
    """Wait for all documents to finish processing. In our backend, chunking happens synchronously during upload, so we just verify they exist."""
    print(f"Waiting for ingestion of {len(docs)} documents (timeout={timeout}s)...")
    start_time = time.time()
    
    pending_docs = {doc['id'] for doc in docs}
    doc_stats = {}
    
    while pending_docs:
        if time.time() - start_time > timeout:
            print(f"Timeout reached ({timeout}s) waiting for ingestion.")
            break
            
        for doc_id in list(pending_docs):
            res = await client.get(f"{API_BASE_URL}/documents/{doc_id}")
            if res.status_code == 200:
                doc_data = res.json()
                
                # Fetch benchmark stats (chunk and page counts)
                stats_res = await client.get(f"{API_BASE_URL}/documents/{doc_id}/stats")
                if stats_res.status_code == 200:
                    stats_data = stats_res.json()
                    doc_data["chunk_count"] = stats_data.get("chunk_count", 0)
                    doc_data["page_count"] = stats_data.get("page_count", 0)
                
                pending_docs.remove(doc_id)
                doc_stats[doc_id] = doc_data
                print(f"Document {doc_id} successfully verified. Chunks: {doc_data.get('chunk_count', 0)}, Pages: {doc_data.get('page_count', 0)}")
            else:
                print(f"Warning: Failed to fetch document {doc_id}")
                
        if pending_docs:
            await asyncio.sleep(2)
            
    total_time = time.time() - start_time
    print(f"Ingestion finished in {total_time:.2f}s")
    return doc_stats, total_time

async def wait_for_experiments(client: httpx.AsyncClient, experiment_ids: list[str], timeout: int = 300):
    """Wait for all experiments to finish running."""
    print(f"Waiting for {len(experiment_ids)} experiments to complete (timeout={timeout}s)...")
    start_time = time.time()
    
    pending_exps = set(experiment_ids)
    exp_stats = {}
    
    while pending_exps:
        if time.time() - start_time > timeout:
            print(f"Timeout reached ({timeout}s) waiting for experiments.")
            break
            
        for exp_id in list(pending_exps):
            res = await client.get(f"{API_BASE_URL}/experiments")
            if res.status_code == 200:
                # API doesn't have a direct GET /experiments/{id} that returns status easily,
                # we list all experiments or use the /compare endpoint.
                # Let's use the list endpoint since it returns total_runs, completed_runs, failed_runs
                all_exps = res.json()
                exp_data = next((e for e in all_exps if e['id'] == exp_id), None)
                
                if exp_data:
                    total = exp_data.get("total_runs", 0)
                    completed = exp_data.get("completed_runs", 0)
                    failed = exp_data.get("failed_runs", 0)
                    
                    if total > 0 and (completed + failed) == total:
                        pending_exps.remove(exp_id)
                        exp_stats[exp_id] = exp_data
                        print(f"Experiment {exp_id} finished ({completed} completed, {failed} failed).")
            else:
                print(f"Warning: Failed to fetch experiments")
                
        if pending_exps:
            await asyncio.sleep(5)
            
    total_time = time.time() - start_time
    print(f"Experiments finished in {total_time:.2f}s")
    return exp_stats, total_time

async def collect_platform_metrics(client: httpx.AsyncClient, world_id: str, doc_stats: dict, exp_stats: dict):
    # This will aggregate all metrics for the report generator.
    
    total_docs = len(doc_stats)
    total_chunks = sum(d.get("chunk_count", 0) for d in doc_stats.values())
    total_pages = sum(d.get("page_count", 0) for d in doc_stats.values())
    
    total_experiments = len(exp_stats)
    total_runs = sum(e.get("total_runs", 0) for e in exp_stats.values())
    
    # We need to gather runs to get average latency, score, etc.
    runs_res = await client.get(f"{API_BASE_URL}/evaluation-runs")
    all_runs = runs_res.json()
    
    # Filter runs for this benchmark
    benchmark_runs = [r for r in all_runs if r.get("experiment_id") in exp_stats]
    
    successful_runs = [r for r in benchmark_runs if r.get("status") == "completed"]
    failed_runs = [r for r in benchmark_runs if r.get("status") == "failed"]
    
    num_success = max(1, len(successful_runs))
    avg_latency = sum(r.get("latency_ms", 0) or 0 for r in successful_runs) / num_success
    avg_score = sum(r.get("overall_score", 0) or 0 for r in successful_runs) / num_success
    avg_accuracy = sum(r.get("accuracy", 0) or 0 for r in successful_runs) / num_success
    avg_groundedness = sum(r.get("groundedness", 0) or 0 for r in successful_runs) / num_success
    avg_retrieval = sum(r.get("retrieval_score", 0) or 0 for r in successful_runs) / num_success
    avg_hallucination = sum(r.get("hallucination_score", 0) or 0 for r in successful_runs) / num_success
    
    # Calculate tokens based on all runs, or just success? We can use all runs since tokens were consumed.
    avg_tokens = sum(r.get("total_tokens", 0) or 0 for r in benchmark_runs) / max(1, len(benchmark_runs))
    prompt_tokens = sum(r.get("prompt_tokens", 0) or 0 for r in benchmark_runs)
    completion_tokens = sum(r.get("completion_tokens", 0) or 0 for r in benchmark_runs)
    
    success_rate = len(successful_runs) / max(1, len(benchmark_runs)) * 100
    
    # P95 latency
    latencies = sorted([r.get("latency_ms", 0) or 0 for r in successful_runs])
    p95_latency = latencies[int(len(latencies) * 0.95)] if latencies else 0
    
    metrics = {
        "ingestion": {
            "documents_processed": total_docs,
            "pages_processed": total_pages,
            "chunks_generated": total_chunks,
        },
        "evaluation": {
            "experiments_executed": total_experiments,
            "runs_executed": total_runs,
            "average_score": avg_score,
            "accuracy": avg_accuracy,
            "groundedness": avg_groundedness,
            "retrieval_score": avg_retrieval,
            "hallucination": avg_hallucination,
            "successful_runs": len(successful_runs),
            "failed_runs": len(failed_runs)
        },
        "model": {
            "average_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "average_tokens": avg_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "success_rate_percent": success_rate,
        },
        "benchmark_runs": benchmark_runs,
        "exp_stats": exp_stats
    }
    return metrics
