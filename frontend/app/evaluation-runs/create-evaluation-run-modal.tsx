"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  task_id: z.string().min(1, "Task is required"),
  model_name: z.string().optional(),
});

type Task = {
  id: string;
  world_id: string;
  title: string;
};

export function CreateEvaluationRunModal({ onSuccess }: { onSuccess: () => void }) {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      task_id: "",
      model_name: "",
    },
  });

  useEffect(() => {
    if (open) {
      fetch("http://localhost:8000/api/v1/tasks")
        .then((res) => res.json())
        .then((data) => setTasks(data))
        .catch(() => {
          toast({
            variant: "destructive",
            title: "Error",
            description: "Failed to load tasks.",
          });
        });
    }
  }, [open, toast]);

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    try {
      const selectedTask = tasks.find((t) => t.id === values.task_id);
      if (!selectedTask) {
        throw new Error("Invalid task selected");
      }

      const payload = {
        ...values,
        world_id: selectedTask.world_id,
      };

      const response = await fetch("http://localhost:8000/api/v1/evaluation-runs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to create evaluation run");
      }

      toast({
        title: "Success",
        description: "Evaluation run created successfully.",
      });
      form.reset();
      setOpen(false);
      onSuccess();
    } catch {
      toast({
        variant: "destructive",
        title: "Error",
        description: "There was a problem creating the evaluation run.",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Evaluation Run
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>New Evaluation Run</DialogTitle>
          <DialogDescription>
            Start a new evaluation run for a specific benchmark task.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="task_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Task</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a task" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {tasks.map((task) => (
                        <SelectItem key={task.id} value={task.id}>
                          {task.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="model_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Model (Optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="gpt-4o, claude-sonnet-4-5" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Start Evaluation
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
