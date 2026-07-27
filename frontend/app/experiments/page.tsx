"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PageShell } from "@/components/page-shell";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Beaker, Calendar, CheckCircle2, Clock, Cpu, ServerCrash, Trophy, XCircle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

/* eslint-disable @typescript-eslint/no-explicit-any */
type Experiment = {
  id: string;
  name: string;
  description: string | null;
  task_name: string;
  created_at: string;
  updated_at: string;
  status: string;
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  best_overall_score: number | null;
  models: string[];
};

export default function ExperimentsPage() {
  const router = useRouter();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExperiments = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/experiments");
      if (!res.ok) {
        throw new Error("Failed to fetch experiments");
      }
      const data = await res.json();
      setExperiments(data);
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
    fetchExperiments();
    
    // Auto refresh while any experiment is pending or running
    const interval = setInterval(() => {
      setExperiments(prev => {
        const hasPending = prev.some(exp => exp.status === 'pending' || exp.status === 'running');
        if (hasPending) {
          fetchExperiments();
        }
        return prev;
      });
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="default" className="bg-green-500 hover:bg-green-600"><CheckCircle2 className="mr-1 h-3 w-3" /> Completed</Badge>;
      case "failed":
        return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" /> Failed</Badge>;
      case "partial":
        return <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20"><CheckCircle2 className="mr-1 h-3 w-3" /> Partial</Badge>;
      case "running":
        return <Badge variant="default" className="bg-blue-500 hover:bg-blue-600 animate-pulse"><Clock className="mr-1 h-3 w-3" /> Running</Badge>;
      case "pending":
      default:
        return <Badge variant="outline"><Clock className="mr-1 h-3 w-3" /> Pending</Badge>;
    }
  };

  if (isLoading && experiments.length === 0) {
    return (
      <PageShell label="Experiments" title="Historical Benchmarks" description="Compare models side-by-side across various tasks.">
        <div className="flex h-[400px] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-r-transparent" />
        </div>
      </PageShell>
    );
  }

  if (error && experiments.length === 0) {
    return (
      <PageShell label="Error" title="Failed to Load" description="">
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading experiments</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={fetchExperiments} variant="outline">
            Try Again
          </Button>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell label="Experiments" title="Historical Benchmarks" description="Review side-by-side model comparisons and evaluations.">
      {experiments.length === 0 ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 rounded-xl border border-dashed text-center">
          <Beaker className="h-12 w-12 text-muted-foreground" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">No experiments yet</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Run an experiment on any task to see side-by-side model benchmarks here.
            </p>
          </div>
          <Button onClick={() => router.push('/tasks')}>
            Browse Tasks
          </Button>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {experiments.map((exp) => (
            <Card key={exp.id} className="flex flex-col flex-1 shadow-sm transition-all hover:shadow-md">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl line-clamp-1">{exp.name}</CardTitle>
                    <CardDescription className="line-clamp-1 mt-1">
                      Task: <span className="font-medium text-foreground">{exp.task_name}</span>
                    </CardDescription>
                  </div>
                  {getStatusBadge(exp.status)}
                </div>
              </CardHeader>
              <CardContent className="pb-4 flex-1">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-1">
                    <p className="text-muted-foreground flex items-center gap-1">
                      <Cpu className="h-3 w-3" /> Models
                    </p>
                    <p className="font-medium">
                      {exp.models.length > 0 ? (
                        <span title={exp.models.join(", ")}>{exp.models.length} Models</span>
                      ) : (
                        "None"
                      )}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-muted-foreground flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" /> Completed
                    </p>
                    <p className="font-medium">
                      {exp.completed_runs} / {exp.total_runs}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-muted-foreground flex items-center gap-1">
                      <Trophy className="h-3 w-3" /> Best Score
                    </p>
                    <p className="font-medium">
                      {exp.best_overall_score !== null ? exp.best_overall_score : "-"}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-muted-foreground flex items-center gap-1">
                      <Calendar className="h-3 w-3" /> Created
                    </p>
                    <p className="font-medium">
                      {formatDistanceToNow(new Date(exp.created_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="pt-4 border-t bg-muted/20">
                <Button 
                  variant={exp.status === "pending" || exp.status === "running" ? "secondary" : "default"} 
                  className="w-full gap-2"
                  onClick={() => router.push(`/experiments/${exp.id}`)}
                >
                  View Comparison <ArrowRight className="h-4 w-4" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </PageShell>
  );
}
