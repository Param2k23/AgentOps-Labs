"use client";

import { useState, useEffect } from "react";
import { Play } from "lucide-react";
import { useRouter } from "next/navigation";
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
import { Label } from "@/components/ui/label";

interface ModelInfo {
  id: string;
  display_name: string;
  provider: string;
  enabled: boolean;
  supports_judge: boolean;
}

interface PromptTemplate {
  id: string;
  name: string;
  version: number;
  is_default: boolean;
}

interface RunEvaluationModalProps {
  task: {
    id: string;
    world_id: string;
    title: string;
  };
  onSuccess: () => void;
}

export function RunEvaluationModal({ task, onSuccess }: RunEvaluationModalProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    if (open) {
      fetchModels();
      fetchTemplates();
    }
  }, [open]);

  const fetchModels = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/models");
      if (res.ok) {
        const data = await res.json();
        setModels(data);
        if (data.length > 0 && selectedModels.length === 0) {
          setSelectedModels([data[0].id]);
        }
      }
    } catch (err) {
      console.error("Failed to fetch models", err);
    }
  };

  const fetchTemplates = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/prompt-templates");
      if (res.ok) {
        const data = await res.json();
        setTemplates(data);
        const def = data.find((t: PromptTemplate) => t.is_default);
        if (def) {
          setSelectedTemplate(def.id);
        } else if (data.length > 0) {
          setSelectedTemplate(data[0].id);
        }
      }
    } catch (err) {
      console.error("Failed to fetch templates", err);
    }
  };

  const toggleModel = (modelId: string) => {
    setSelectedModels(prev => 
      prev.includes(modelId) 
        ? prev.filter(id => id !== modelId) 
        : [...prev, modelId]
    );
  };

  const handleRunExperiment = async () => {
    if (selectedModels.length === 0) {
      toast({ title: "Error", description: "Select at least one model", variant: "destructive" });
      return;
    }
    
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/experiments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: `Experiment: ${task.title}`,
          task_id: task.id,
          models: selectedModels,
          prompt_template_id: selectedTemplate || null,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to start experiment.");
      }

      const experiment = await res.json();

      toast({
        title: "Experiment Started",
        description: "The evaluation runs are processing in the background.",
      });

      setOpen(false);
      onSuccess();
      router.push(`/experiments/${experiment.id}`);
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
          <Play className="h-4 w-4" /> Run Experiment
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Start Experiment</DialogTitle>
          <DialogDescription>
            Select multiple models to evaluate and compare their performance side-by-side.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="space-y-3 border rounded-md p-4 bg-card">
            <Label>Select Models</Label>
            <div className="flex flex-col gap-2 mt-2">
              {models.length === 0 && <span className="text-sm text-muted-foreground">Loading models...</span>}
              {models.map((model) => (
                <label key={model.id} className="flex items-center gap-2 cursor-pointer text-sm">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300"
                    checked={selectedModels.includes(model.id)}
                    onChange={() => toggleModel(model.id)}
                  />
                  {model.display_name}
                </label>
              ))}
            </div>
          </div>
          
          <div className="space-y-3 border rounded-md p-4 bg-card">
            <Label>Prompt Template</Label>
            <select
              className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
            >
              <option value="" disabled>Select a template</option>
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.name} (v{t.version}){t.is_default ? ' - Default' : ''}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleRunExperiment} disabled={loading || selectedModels.length === 0} className="gap-2">
            {loading ? <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-r-transparent" /> : <Play className="h-4 w-4" />}
            {loading ? "Starting..." : "Run Experiment"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
