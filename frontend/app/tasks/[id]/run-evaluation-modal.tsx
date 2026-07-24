"use client";

import { useState } from "react";
import { Play } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

interface RunEvaluationModalProps {
  task: {
    id: string;
    world_id: string;
  };
  onSuccess: () => void;
}

export function RunEvaluationModal({ task, onSuccess }: RunEvaluationModalProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("gemini-2.5-flash");
  const { toast } = useToast();

  const handleRunEvaluation = async () => {
    setLoading(true);
    try {
      // 1. Create the Evaluation Run record
      const createRes = await fetch("http://localhost:8000/api/v1/evaluation-runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: task.id,
          world_id: task.world_id,
          model_name: model,
        }),
      });

      if (!createRes.ok) {
        throw new Error("Failed to create evaluation run.");
      }

      const runData = await createRes.json();
      const runId = runData.id;

      // 2. Trigger the Execution
      const execRes = await fetch(`http://localhost:8000/api/v1/evaluation-runs/${runId}/execute`, {
        method: "POST",
      });

      if (!execRes.ok) {
        throw new Error("Failed to execute evaluation run.");
      }

      toast({
        title: "Evaluation Complete",
        description: "The evaluation run has finished successfully.",
      });

      setOpen(false);
      onSuccess();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred.";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="w-full mt-4 gap-2">
          <Play className="h-4 w-4" /> Run Evaluation
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Start Evaluation</DialogTitle>
          <DialogDescription>
            This will trigger the full AI pipeline using the context chunks for this task.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="model">Model</Label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger id="model">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gemini-2.5-flash">Gemini 2.5 Flash</SelectItem>
                <SelectItem value="gemini-2.5-pro">Gemini 2.5 Pro</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="text-sm text-muted-foreground mt-2 border rounded-md p-3 bg-muted/20">
            <p><strong>Note:</strong> Temperature and top-k are configured globally for this milestone.</p>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleRunEvaluation} disabled={loading} className="gap-2">
            {loading ? <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-r-transparent" /> : <Play className="h-4 w-4" />}
            {loading ? "Running..." : "Start"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
