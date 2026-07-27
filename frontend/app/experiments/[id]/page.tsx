"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, ServerCrash } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { Button } from "@/components/ui/button";

import { ComparisonTable } from "@/components/experiments/ComparisonTable";
import { Charts } from "@/components/experiments/Charts";
import { WinnerCards } from "@/components/experiments/WinnerCards";

/* eslint-disable @typescript-eslint/no-explicit-any */
type ExperimentData = {
  experiment: Record<string, any>;
  runs: Record<string, any>[];
  summary: Record<string, any>;
};

export default function ExperimentDashboardPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  
  const [data, setData] = useState<ExperimentData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExperiment = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/experiments/${id}/compare`);
      if (!res.ok) {
        throw new Error("Failed to fetch experiment details");
      }
      const jsonData = await res.json();
      setData(jsonData);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchExperiment();
      
      // Auto refresh while any run is pending or running
      const interval = setInterval(() => {
        setData(prev => {
          if (!prev) return prev;
          const hasPending = prev.runs.some(r => r.status === 'pending' || r.status === 'running');
          if (hasPending) {
            fetchExperiment();
          }
          return prev;
        });
      }, 5000);
      
      return () => clearInterval(interval);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }
  }, [id]);

  if (isLoading && !data) {
    return (
      <PageShell label="Experiment Details" title="Loading..." description="">
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </PageShell>
    );
  }

  if (error || !data) {
    return (
      <PageShell label="Error" title="Failed to Load" description="">
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading experiment</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={() => router.push("/tasks")} variant="outline">
            Back to Tasks
          </Button>
        </div>
      </PageShell>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => router.push(`/tasks/${data.experiment.task_id}`)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{data.experiment.name}</h1>
          <p className="text-sm text-muted-foreground">Experiment Benchmarking Dashboard</p>
        </div>
      </div>

      <WinnerCards summary={data.summary} />

      <div className="grid gap-6 md:grid-cols-2">
        <div className="col-span-1 md:col-span-2">
          <Charts runs={data.runs} />
        </div>
        
        <div className="col-span-1 md:col-span-2">
          <ComparisonTable runs={data.runs} onRowClick={(runId) => router.push(`/evaluation-runs/${runId}`)} />
        </div>
      </div>
    </div>
  );
}
