import matplotlib.pyplot as plt
import os

def generate_charts(metrics: dict):
    print("Generating charts...")
    out_dir = os.path.dirname(__file__)
    
    runs = metrics.get("benchmark_runs", [])
    if not runs:
        print("No runs available to generate charts.")
        return
        
    models = list(set(r.get("model_name", "Unknown") for r in runs if r.get("model_name")))
    if not models:
        return
        
    avg_latency = []
    avg_score = []
    avg_tokens = []
    avg_cost = [] # Simulated cost if not provided directly
    
    for m in models:
        m_runs = [r for r in runs if r.get("model_name") == m]
        n = max(1, len(m_runs))
        avg_latency.append(sum(r.get("latency_ms") or 0 for r in m_runs) / n)
        avg_score.append(sum(r.get("overall_score") or 0 for r in m_runs) / n)
        avg_tokens.append(sum(r.get("total_tokens") or 0 for r in m_runs) / n)
        avg_cost.append(sum(r.get("total_tokens") or 0 for r in m_runs) * 0.0001 / n) # arbitrary cost multiplier
        
    # Latency Chart
    plt.figure(figsize=(8, 5))
    plt.bar(models, avg_latency, color='skyblue')
    plt.title('Average Latency per Model (ms)')
    plt.ylabel('Latency (ms)')
    plt.savefig(os.path.join(out_dir, 'latency.png'))
    plt.close()
    
    # Scores Chart
    plt.figure(figsize=(8, 5))
    plt.bar(models, avg_score, color='lightgreen')
    plt.title('Average Overall Score per Model')
    plt.ylabel('Score (0-100)')
    plt.ylim(0, 100)
    plt.savefig(os.path.join(out_dir, 'scores.png'))
    plt.close()
    
    # Tokens Chart
    plt.figure(figsize=(8, 5))
    plt.bar(models, avg_tokens, color='salmon')
    plt.title('Average Tokens per Model')
    plt.ylabel('Total Tokens')
    plt.savefig(os.path.join(out_dir, 'tokens.png'))
    plt.close()
    
    # Cost Chart
    plt.figure(figsize=(8, 5))
    plt.bar(models, avg_cost, color='gold')
    plt.title('Estimated Cost per Run ($)')
    plt.ylabel('Cost')
    plt.savefig(os.path.join(out_dir, 'cost.png'))
    plt.close()
    
    # Leaderboard Placeholder
    plt.figure(figsize=(8, 5))
    sorted_models = [x for _, x in sorted(zip(avg_score, models), reverse=True)]
    sorted_scores = sorted(avg_score, reverse=True)
    plt.bar(sorted_models, sorted_scores, color='mediumpurple')
    plt.title('Leaderboard (Ranked by Score)')
    plt.ylabel('Score (0-100)')
    plt.ylim(0, 100)
    plt.savefig(os.path.join(out_dir, 'leaderboard.png'))
    plt.close()
    
    print("Charts generated successfully.")
