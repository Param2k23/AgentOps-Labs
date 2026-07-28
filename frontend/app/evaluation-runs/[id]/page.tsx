"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader2, ServerCrash, ArrowLeft, BarChart3, Clock, Cpu, Hash } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

type EvaluationRun = {
  id: string;
  task_id: string;
  world_id: string;
  prompt_template_name?: string | null;
  prompt_template_version?: number | null;
  model_name?: string;
  status: string;
  accuracy?: number;
  groundedness?: number;
  citation_score?: number;
  retrieval_score?: number;
  hallucination_score?: number;
  tool_success?: number;
  overall_score?: number;
  feedback?: string;
  response?: string;
  latency_ms?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  error_message?: string;
  created_at: string;
};

// Helper for progress bar color
const getScoreColor = (score: number | undefined) => {
  if (score === undefined || score === null) return "bg-muted";
  if (score >= 90) return "bg-green-500";
  if (score >= 70) return "bg-yellow-500";
  return "bg-red-500";
};

export default function EvaluationRunDetailsPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  
  const [run, setRun] = useState<EvaluationRun | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRun = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/evaluation-runs/${id}`);
      if (!res.ok) {
        throw new Error("Failed to fetch evaluation run details");
      }
      const data = await res.json();
      setRun(data);
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
      fetchRun();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (isLoading) {
    return (
      <PageShell label="Evaluation Run" title="Loading..." description="">
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </PageShell>
    );
  }

  if (error || !run) {
    return (
      <PageShell label="Error" title="Failed to Load" description="">
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading evaluation run</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={() => router.back()} variant="outline">
            Go Back
          </Button>
        </div>
      </PageShell>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => router.push(`/tasks/${run.task_id}`)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Run Details</h1>
          <p className="text-sm text-muted-foreground">ID: {run.id}</p>
        </div>
        <div className="ml-auto flex gap-2">
          <Badge 
            variant={
              run.status === "completed" ? "default" : 
              ["failed", "provider_error", "invalid_api_key"].includes(run.status) ? "destructive" : 
              ["rate_limited", "timeout"].includes(run.status) ? "outline" : "secondary"
            } 
            className={`uppercase ${["rate_limited", "timeout"].includes(run.status) ? "border-orange-500 text-orange-500" : ""}`}
          >
            {run.status.replace("_", " ")}
          </Badge>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Model</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.model_name || "Unknown"}</div>
            {run.prompt_template_name && (
              <p className="text-xs text-muted-foreground mt-1">
                Prompt: {run.prompt_template_name} v{run.prompt_template_version}
              </p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Latency</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.latency_ms ? `${run.latency_ms} ms` : "-"}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tokens Used</CardTitle>
            <Hash className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.total_tokens || "-"}</div>
          </CardContent>
        </Card>
        <Card className={run.overall_score !== null && run.overall_score! >= 90 ? "border-green-500/50 bg-green-500/10" : ""}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Score</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.overall_score ?? "-"}</div>
          </CardContent>
        </Card>
      </div>

      {run.status === "completed" && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Detailed Scores Card */}
          <Card>
            <CardHeader>
              <CardTitle>Metric Breakdown</CardTitle>
              <CardDescription>Detailed scores provided by LLM-as-a-Judge</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                { label: "Accuracy", value: run.accuracy },
                { label: "Groundedness", value: run.groundedness },
                { label: "Citation Score", value: run.citation_score },
                { label: "Retrieval Score", value: run.retrieval_score },
                { label: "Hallucination Score", value: run.hallucination_score },
              ].map((metric) => (
                <div key={metric.label} className="space-y-2">
                  <div className="flex justify-between text-sm font-medium">
                    <span>{metric.label}</span>
                    <span>{metric.value ?? "-"}</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                    <div
                      className={`h-full ${getScoreColor(metric.value)}`}
                      style={{ width: `${metric.value ?? 0}%` }}
                    />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Feedback & Response Card */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Judge Feedback</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {run.feedback || "No feedback provided."}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Generated Response</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-wrap bg-muted/30 p-4 rounded-md border">
                  {run.response || "No response generated."}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {["failed", "provider_error", "invalid_api_key", "rate_limited", "timeout"].includes(run.status) && (
        <Card className={["rate_limited", "timeout"].includes(run.status) ? "border-orange-500" : "border-destructive"}>
          <CardHeader>
            <CardTitle className={["rate_limited", "timeout"].includes(run.status) ? "text-orange-500" : "text-destructive"}>Execution Failed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {run.error_message || run.feedback || "An unknown error occurred during execution."}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
