import json
import csv
import os

def generate_reports(metrics: dict):
    print("Generating reports...")
    out_dir = os.path.dirname(__file__)
    
    # JSON Report
    json_path = os.path.join(out_dir, "benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    # CSV Report (Summary of runs)
    csv_path = os.path.join(out_dir, "benchmark_results.csv")
    runs = metrics.get("benchmark_runs", [])
    if runs:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["id", "experiment_id", "model_name", "status", "overall_score", "latency_ms", "total_tokens"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in runs:
                writer.writerow(r)
                
    # Markdown Report (Resume Metrics)
    md_path = os.path.join(out_dir, "BENCHMARK.md")
    
    ingestion = metrics.get("ingestion", {})
    eval_metrics = metrics.get("evaluation", {})
    model_metrics = metrics.get("model", {})
    
    models = list(set(r.get("model_name", "Unknown") for r in runs if r.get("model_name")))
    prompt_templates = list(set(r.get("prompt_template_id", "Default") for r in runs if r.get("prompt_template_id")))
    
    content = f"""# Benchmark & Validation Report

## Executive Summary
This automated benchmark was executed to validate the platform's performance, stability, and evaluation capabilities.

### Platform Statistics (Resume Metrics)
- **Documents Processed:** {ingestion.get('documents_processed', 0)}
- **Pages Parsed:** {ingestion.get('pages_processed', 0)}
- **Chunks Created:** {ingestion.get('chunks_generated', 0)}
- **Average Chunk Size:** 500 (Configured)
- **Tasks Generated:** {eval_metrics.get('runs_executed', 0) // len(models) if len(models) > 0 else 0}
- **Experiments Executed:** {eval_metrics.get('experiments_executed', 0)}
- **Evaluation Runs:** {eval_metrics.get('runs_executed', 0)}
- **Prompt Templates Tested:** {len(prompt_templates)}
- **Models Compared:** {len(models)}
- **Successful Runs:** {eval_metrics.get('successful_runs', 0)}
- **Failed Runs:** {eval_metrics.get('failed_runs', 0)}
- **Success Rate:** {model_metrics.get('success_rate_percent', 0):.2f}%

### Performance Metrics
- **Average Latency:** {model_metrics.get('average_latency_ms', 0):.2f} ms
- **P95 Latency:** {model_metrics.get('p95_latency_ms', 0):.2f} ms
- **Tokens Processed (Total):** {model_metrics.get('prompt_tokens', 0) + model_metrics.get('completion_tokens', 0)}
- **Prompt Tokens:** {model_metrics.get('prompt_tokens', 0)}
- **Completion Tokens:** {model_metrics.get('completion_tokens', 0)}
- **Estimated Cost:** $0.00 (Using Free Tier Models)

### Evaluation Scores (Average)
- **Overall Score:** {eval_metrics.get('average_score', 0):.2f}/100
- **Accuracy:** {eval_metrics.get('accuracy', 0):.2f}/100
- **Groundedness:** {eval_metrics.get('groundedness', 0):.2f}/100
- **Retrieval Score:** {eval_metrics.get('retrieval_score', 0):.2f}/100
- **Hallucination:** {eval_metrics.get('hallucination', 0):.2f}/100

## Detailed Execution Stats

## Visualizations
*(Note: These charts are automatically generated and saved in the benchmark directory)*
- `leaderboard.png`: Ranks models by overall score
- `latency.png`: Average latency across models
- `tokens.png`: Average token usage across models
- `scores.png`: Average evaluation scores across models
- `cost.png`: Estimated cost evaluation
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Reports generated successfully.")
