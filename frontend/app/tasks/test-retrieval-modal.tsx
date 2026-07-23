"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
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

type Chunk = {
  chunk_index: number;
  text: string;
  score: number;
};

interface TestRetrievalModalProps {
  taskId: string;
  taskTitle: string;
}

export function TestRetrievalModal({ taskId, taskTitle }: TestRetrievalModalProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const handleTestRetrieval = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/retrieval?top_k=3`);
      if (!res.ok) {
        throw new Error("Failed to fetch retrieval chunks. Make sure the document has chunks rebuilt.");
      }
      const data = await res.json();
      setChunks(data);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred";
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen);
    if (newOpen) {
      handleTestRetrieval();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" title="Test Retrieval">
          <Search className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Test Retrieval: {taskTitle}</DialogTitle>
          <DialogDescription>
            Retrieving top 3 chunks for this task using deterministic mock search.
          </DialogDescription>
        </DialogHeader>
        
        {loading ? (
          <div className="flex h-32 items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="text-center p-4 text-destructive border rounded">
            <p>{error}</p>
          </div>
        ) : chunks.length === 0 ? (
          <div className="text-center p-8 text-muted-foreground border rounded">
            No chunks found. Check if the task is associated with a document and if the document has chunks.
          </div>
        ) : (
          <div className="space-y-4 mt-4">
            <div className="text-sm font-medium">Found {chunks.length} chunks</div>
            {chunks.map((chunk, idx) => (
              <div key={idx} className="border rounded-md p-4 space-y-2 relative bg-muted/20">
                <div className="flex justify-between items-center text-xs text-muted-foreground">
                  <span>Chunk Index: {chunk.chunk_index}</span>
                  <span className="bg-primary/10 text-primary px-2 py-1 rounded">Score: {chunk.score.toFixed(4)}</span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{chunk.text}</p>
              </div>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
