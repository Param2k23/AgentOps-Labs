"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { Loader2, Edit2, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

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

interface EditTaskFormProps {
  task: Task;
  onUpdate: (updatedTask: Task) => void;
}

export function EditTaskForm({ task, onUpdate }: EditTaskFormProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const { register, handleSubmit, reset } = useForm({
    defaultValues: {
      description: task.description || "",
      ground_truth: task.ground_truth || "",
      rubric: task.rubric || "",
      expected_output: task.expected_output || "",
      metadata: task.metadata ? JSON.stringify(task.metadata, null, 2) : "",
    },
  });

  const onSubmit = async (values: Record<string, unknown>) => {
    setIsLoading(true);
    try {
      let parsedMetadata = undefined;
      if (values.metadata) {
        try {
          parsedMetadata = JSON.parse(values.metadata as string);
        } catch {
          throw new Error("Invalid JSON in Metadata field");
        }
      }

      const payload = {
        description: values.description,
        ground_truth: values.ground_truth,
        rubric: values.rubric,
        expected_output: values.expected_output,
        metadata: parsedMetadata,
      };

      const res = await fetch(`http://localhost:8000/api/v1/tasks/${task.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("Failed to update task");
      }

      const updatedTask = await res.json();
      onUpdate(updatedTask);
      setIsEditing(false);
      toast({
        title: "Task Updated",
        description: "Your changes have been saved.",
      });
    } catch (err: unknown) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to update task",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const cancelEdit = () => {
    reset({
      description: task.description || "",
      ground_truth: task.ground_truth || "",
      rubric: task.rubric || "",
      expected_output: task.expected_output || "",
      metadata: task.metadata ? JSON.stringify(task.metadata, null, 2) : "",
    });
    setIsEditing(false);
  };

  if (!isEditing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold leading-none tracking-tight">Configuration</h3>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
              <Edit2 className="h-4 w-4 mr-2" /> Edit
            </Button>
          </div>
        </div>
        <div className="text-sm text-muted-foreground space-y-4">
          <div>
            <Label className="font-semibold text-foreground block mb-1">Description</Label>
            <p className="whitespace-pre-wrap">{task.description || "N/A"}</p>
          </div>
          <div>
            <Label className="font-semibold text-foreground block mb-1">Ground Truth</Label>
            <p className="whitespace-pre-wrap">{task.ground_truth || "N/A"}</p>
          </div>
          <div>
            <Label className="font-semibold text-foreground block mb-1">Rubric</Label>
            <p className="whitespace-pre-wrap">{task.rubric || "N/A"}</p>
          </div>
          <div>
            <Label className="font-semibold text-foreground block mb-1">Expected Output</Label>
            <p className="whitespace-pre-wrap">{task.expected_output || "N/A"}</p>
          </div>
          {task.metadata && (
            <div>
              <Label className="font-semibold text-foreground block mb-1">Metadata</Label>
              <pre className="p-2 bg-muted/30 rounded-md overflow-x-auto">
                {JSON.stringify(task.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold leading-none tracking-tight">Edit Configuration</h3>
        <div className="flex items-center gap-2">
          <Button type="button" variant="ghost" size="sm" onClick={cancelEdit} disabled={isLoading}>
            <X className="h-4 w-4 mr-2" /> Cancel
          </Button>
          <Button type="submit" size="sm" disabled={isLoading}>
            {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Check className="h-4 w-4 mr-2" />}
            Save
          </Button>
        </div>
      </div>
      
      <div className="space-y-4">
        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea id="description" {...register("description")} rows={3} placeholder="Task description..." className="mt-1" />
        </div>
        <div>
          <Label htmlFor="ground_truth">Ground Truth</Label>
          <Textarea id="ground_truth" {...register("ground_truth")} rows={3} placeholder="Reference answer..." className="mt-1" />
        </div>
        <div>
          <Label htmlFor="rubric">Rubric</Label>
          <Textarea id="rubric" {...register("rubric")} rows={3} placeholder="Scoring criteria..." className="mt-1" />
        </div>
        <div>
          <Label htmlFor="expected_output">Expected Output</Label>
          <Textarea id="expected_output" {...register("expected_output")} rows={3} placeholder="Expected format..." className="mt-1" />
        </div>
        <div>
          <Label htmlFor="metadata">Metadata (JSON)</Label>
          <Textarea id="metadata" {...register("metadata")} rows={4} placeholder='{"key": "value"}' className="mt-1 font-mono text-xs" />
        </div>
      </div>
    </form>
  );
}
