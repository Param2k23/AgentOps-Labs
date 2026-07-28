import asyncio
import httpx
from .dataset_loader import generate_datasets
from .world_generator import generate_world_and_upload
from .task_generator import generate_and_upload_tasks
from .experiment_runner import run_experiments
from .metrics_collector import wait_for_ingestion, wait_for_experiments, collect_platform_metrics
from .charts import generate_charts
from .report_generator import generate_reports

async def main():
    print("========================================")
    print("  Enterprise Agent Lab - Benchmark Suite")
    print("========================================")
    
    # Stage 1: Generate or load datasets
    await generate_datasets()
    
    # Stage 2: Create World and Upload Documents
    world_id, docs = await generate_world_and_upload()
    if not world_id or not docs:
        print("Failed to initialize world/documents. Aborting benchmark.")
        return
        
    async with httpx.AsyncClient(timeout=300.0) as client:
        print("\n=== Stage 3: Waiting for Ingestion ===")
        doc_stats, ingestion_time = await wait_for_ingestion(client, docs)
        
        print("\n=== Stage 4: Generating Tasks ===")
        tasks = await generate_and_upload_tasks(world_id, docs)
        if not tasks:
            print("No tasks generated. Aborting benchmark.")
            return
            
        print("\n=== Stage 5: Running Experiments ===")
        experiment_ids = await run_experiments(tasks)
        if not experiment_ids:
            print("No experiments launched. Aborting benchmark.")
            return
            
        print("\n=== Stage 6: Waiting for Completion ===")
        exp_stats, eval_time = await wait_for_experiments(client, experiment_ids)
        
        print("\n=== Stage 7: Collecting Metrics ===")
        metrics = await collect_platform_metrics(client, world_id, doc_stats, exp_stats)
        metrics["ingestion"]["ingestion_time_seconds"] = ingestion_time
        metrics["evaluation"]["evaluation_time_seconds"] = eval_time
        
        # Stage 8: Generate Reports & Charts
        generate_charts(metrics)
        generate_reports(metrics)
        
    print("\n========================================")
    print("  Benchmark Suite Completed Successfully!")
    print("  Check BENCHMARK.md and generated charts.")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(main())
