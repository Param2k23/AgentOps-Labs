"use client";

import { useEffect, useState } from "react";
import { Loader2, ServerCrash, Trash2, Activity } from "lucide-react";
import { CreateEvaluationRunModal } from "./create-evaluation-run-modal";
import { useToast } from "@/hooks/use-toast";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageShell } from "@/components/page-shell";

type EvaluationRun = {
  id: string;
  task_id: string;
  world_id: string;
  model_name?: string;
  status: string;
  overall_score?: number;
  created_at: string;
};

export default function EvaluationRunsPage() {
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchRuns = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/evaluation-runs");
      if (!res.ok) {
        throw new Error("Failed to fetch evaluation runs");
      }
      const data = await res.json();
      setRuns(data);
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
    fetchRuns();
  }, []);

  const deleteRun = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/evaluation-runs/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        throw new Error("Failed to delete evaluation run");
      }
      toast({
        title: "Deleted",
        description: "The evaluation run has been deleted.",
      });
      fetchRuns();
    } catch {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to delete evaluation run.",
      });
    }
  };

  return (
    <PageShell
      label="Evaluation Runs"
      title="Evaluation Runs"
      description="Quality measurement and metrics for agent executions."
    >
      <div className="flex items-center justify-end mb-6 mt-[-60px] relative z-10">
        <CreateEvaluationRunModal onSuccess={fetchRuns} />
      </div>

      {isLoading ? (
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading runs</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={fetchRuns} variant="outline">
            Try again
          </Button>
        </div>
      ) : runs.length === 0 ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 rounded-lg border border-dashed text-center">
          <Activity className="h-12 w-12 text-muted-foreground" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">No runs found</h3>
            <p className="text-sm text-muted-foreground">
              Start a new evaluation run to measure agent performance.
            </p>
          </div>
          <CreateEvaluationRunModal onSuccess={fetchRuns} />
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => (
                <TableRow key={run.id}>
                  <TableCell className="font-medium">
                    {run.model_name ? run.model_name : <span className="text-muted-foreground">Unknown</span>}
                  </TableCell>
                  <TableCell>
                    <Badge variant={run.status === "completed" ? "default" : "secondary"} className="uppercase">
                      {run.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {run.overall_score !== null && run.overall_score !== undefined ? (
                      <span className="font-semibold">{run.overall_score}</span>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(run.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:bg-destructive/10"
                      onClick={() => deleteRun(run.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </PageShell>
  );
}
