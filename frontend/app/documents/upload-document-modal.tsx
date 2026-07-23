"use client";

import { useEffect, useState, useRef } from "react";
import { Loader2, UploadCloud } from "lucide-react";

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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

type World = {
  id: string;
  name: string;
};

export function UploadDocumentModal({ onSuccess }: { onSuccess: () => void }) {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [worlds, setWorlds] = useState<World[]>([]);
  const [selectedWorldId, setSelectedWorldId] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      fetch("http://localhost:8000/api/v1/worlds")
        .then((res) => res.json())
        .then((data) => setWorlds(data))
        .catch(() => {
          toast({
            variant: "destructive",
            title: "Error",
            description: "Failed to load worlds.",
          });
        });
    } else {
      // Reset state when closing
      setFile(null);
      setSelectedWorldId("");
      setDragActive(false);
    }
  }, [open, toast]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedWorldId) {
      toast({
        variant: "destructive",
        title: "Validation Error",
        description: "Please select a world.",
      });
      return;
    }

    if (!file) {
      toast({
        variant: "destructive",
        title: "Validation Error",
        description: "Please select a file to upload.",
      });
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`http://localhost:8000/api/v1/documents/worlds/${selectedWorldId}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Failed to upload document");
      }

      toast({
        title: "Success",
        description: "Document uploaded and ingested successfully.",
      });
      setOpen(false);
      onSuccess();
    } catch (error: unknown) {
      const message =
        error instanceof Error
          ? error.message
          : "There was a problem uploading the document.";

      toast({
        variant: "destructive",
        title: "Error",
        description: message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="default">
          <UploadCloud className="mr-2 h-4 w-4" />
          Upload Document
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>
            Upload a PDF, DOCX, TXT, or Markdown file to ingest into a world.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none">World</label>
            <Select value={selectedWorldId} onValueChange={setSelectedWorldId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a world" />
              </SelectTrigger>
              <SelectContent>
                {worlds.map((world) => (
                  <SelectItem key={world.id} value={world.id}>
                    {world.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div
            className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleChange}
              accept=".pdf,.docx,.txt,.md"
            />
            <UploadCloud className="h-10 w-10 text-muted-foreground mb-4" />
            {file ? (
              <div className="space-y-1">
                <p className="text-sm font-medium">{file.name}</p>
                <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
            ) : (
              <div className="space-y-1">
                <p className="text-sm font-medium">Click to select or drag and drop</p>
                <p className="text-xs text-muted-foreground">PDF, DOCX, TXT, or Markdown</p>
              </div>
            )}
          </div>

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? "Uploading & Ingesting..." : "Upload Document"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
