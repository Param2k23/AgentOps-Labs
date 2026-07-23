"use client";

import { useEffect, useState } from "react";
import { Loader2, ServerCrash, Trash2, ListTodo } from "lucide-react";
import { CreateTaskModal } from "./create-task-modal";
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

type Task = {
  id: string;
  world_id: string;
  document_id?: string;
  title: string;
  difficulty?: string;
  department?: string;
  created_at: string;
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchTasks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/tasks");
      if (!res.ok) {
        throw new Error("Failed to fetch tasks");
      }
      const data = await res.json();
      setTasks(data);
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
    fetchTasks();
  }, []);

  const deleteTask = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/tasks/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        throw new Error("Failed to delete task");
      }
      toast({
        title: "Deleted",
        description: "The task has been deleted.",
      });
      fetchTasks();
    } catch {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to delete task.",
      });
    }
  };

  return (
    <PageShell
      label="Tasks"
      title="Tasks"
      description="Benchmark problems used to evaluate agent performance."
    >
      <div className="flex items-center justify-end mb-6 mt-[-60px] relative z-10">
        <CreateTaskModal onSuccess={fetchTasks} />
      </div>

      {isLoading ? (
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading tasks</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={fetchTasks} variant="outline">
            Try again
          </Button>
        </div>
      ) : tasks.length === 0 ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 rounded-lg border border-dashed text-center">
          <ListTodo className="h-12 w-12 text-muted-foreground" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">No tasks found</h3>
            <p className="text-sm text-muted-foreground">
              Add a new benchmark task to get started.
            </p>
          </div>
          <CreateTaskModal onSuccess={fetchTasks} />
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Difficulty</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Added</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell className="font-medium truncate max-w-[200px]" title={task.title}>
                    {task.title}
                  </TableCell>
                  <TableCell>
                    {task.difficulty ? (
                      <Badge variant="outline" className="uppercase">{task.difficulty}</Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {task.department ? task.department : <span className="text-muted-foreground">-</span>}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(task.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:bg-destructive/10"
                      onClick={() => deleteTask(task.id)}
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
