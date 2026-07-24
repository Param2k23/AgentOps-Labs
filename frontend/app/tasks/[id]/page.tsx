"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader2, ServerCrash, PlaySquare, ArrowLeft } from "lucide-react";
import { PageShell } from "@/components/page-shell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { RunEvaluationModal } from "./run-evaluation-modal";

type Task = {
  id: string;
  world_id: string;
  document_id?: string;
  title: string;
  description?: string;
  difficulty?: string;
  department?: string;
  ground_truth?: string;
  rubric?: string;
  expected_output?: string;
  metadata?: Record<string, unknown> | null;
  created_at: string;
};

type EvaluationRun = {
  id: string;
  task_id: string;
  world_id: string;
  model_name?: string;
  status: string;
  overall_score?: number;
  created_at: string;
};

import { EditTaskForm } from "./edit-task-form";

export default function TaskDetailsPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  
  const [task, setTask] = useState<Task | null>(null);
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTaskAndRuns = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const taskRes = await fetch(`http://localhost:8000/api/v1/tasks/${id}`);
      if (!taskRes.ok) {
        throw new Error("Failed to fetch task details");
      }
      const taskData = await taskRes.json();
      setTask(taskData);

      // In a real app we'd filter runs by task_id in the API, but for now we fetch all and filter
      const runsRes = await fetch("http://localhost:8000/api/v1/evaluation-runs");
      if (runsRes.ok) {
        const allRuns = await runsRes.json();
        setRuns(allRuns.filter((r: EvaluationRun) => r.task_id === id));
      }
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
      fetchTaskAndRuns();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (isLoading) {
    return (
      <PageShell label="Task Details" title="Loading..." description="">
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </PageShell>
    );
  }

  if (error || !task) {
    return (
      <PageShell label="Error" title="Failed to Load" description="">
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading task</h3>
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
        <Button variant="ghost" size="icon" onClick={() => router.push("/tasks")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{task.title}</h1>
          <p className="text-sm text-muted-foreground">Manage this benchmark task and its evaluation history.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 space-y-4">
          <EditTaskForm task={task} onUpdate={setTask} />
        </div>

        <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col items-center justify-center space-y-4 text-center">
          <PlaySquare className="h-10 w-10 text-muted-foreground" />
          <div>
            <h3 className="font-semibold">Test Agent Performance</h3>
            <p className="text-sm text-muted-foreground">Run an evaluation to test the agent on this task.</p>
          </div>
          <RunEvaluationModal task={task} onSuccess={fetchTaskAndRuns} />
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-medium">Evaluation History</h3>
        {runs.length === 0 ? (
          <div className="flex h-[200px] flex-col items-center justify-center rounded-lg border border-dashed text-center">
            <p className="text-sm text-muted-foreground">No evaluations have been run for this task yet.</p>
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Run ID</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.map((run) => (
                  <TableRow 
                    key={run.id} 
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => router.push(`/evaluation-runs/${run.id}`)}
                  >
                    <TableCell className="font-medium truncate max-w-[150px]" title={run.id}>
                      {run.id}
                    </TableCell>
                    <TableCell>
                      {run.model_name ? run.model_name : <span className="text-muted-foreground">Unknown</span>}
                    </TableCell>
                    <TableCell>
                      <Badge variant={run.status === "completed" ? "default" : run.status === "failed" ? "destructive" : "secondary"} className="uppercase">
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
                      {new Date(run.created_at).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
