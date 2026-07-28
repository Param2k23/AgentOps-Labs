"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PageShell } from "@/components/page-shell";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileCode2, Plus, Edit, Copy, Trash2, CheckCircle2 } from "lucide-react";

type PromptTemplate = {
  id: string;
  name: string;
  description: string | null;
  system_prompt: string | null;
  user_prompt_template: string;
  version: number;
  is_default: boolean;
};

export default function PromptTemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/prompt-templates");
      if (!res.ok) throw new Error("Failed to fetch prompt templates");
      const data = await res.json();
      setTemplates(data);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError("An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this prompt template?")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/prompt-templates/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete template");
      fetchTemplates();
    } catch (err) {
      alert("Error deleting template");
    }
  };

  if (isLoading) {
    return (
      <PageShell label="Prompt Library" title="Prompt Engineering" description="Manage templates for evaluating models.">
        <div className="flex h-[400px] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-r-transparent" />
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell label="Prompt Library" title="Prompt Engineering" description="Manage prompt templates for evaluating models.">
      <div className="mb-6 flex justify-end">
        <Button onClick={() => router.push('/prompt-templates/new')} className="gap-2">
          <Plus className="h-4 w-4" /> Create Prompt
        </Button>
      </div>

      {error ? (
        <div className="text-center text-destructive">{error}</div>
      ) : templates.length === 0 ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 rounded-xl border border-dashed text-center">
          <FileCode2 className="h-12 w-12 text-muted-foreground" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">No prompt templates yet</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Create a prompt template to start comparing prompts across different models.
            </p>
          </div>
          <Button onClick={() => router.push('/prompt-templates/new')}>
            Create Prompt
          </Button>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => (
            <Card key={template.id} className="flex flex-col flex-1 shadow-sm transition-all hover:shadow-md">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl line-clamp-1">{template.name}</CardTitle>
                    <CardDescription className="line-clamp-2 mt-1 min-h-[40px]">
                      {template.description || "No description provided."}
                    </CardDescription>
                  </div>
                  {template.is_default && (
                    <Badge variant="default" className="bg-green-500 hover:bg-green-600">
                      <CheckCircle2 className="mr-1 h-3 w-3" /> Default
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="pb-4 flex-1">
                <div className="space-y-1 text-sm">
                  <p className="text-muted-foreground flex items-center gap-1">
                    Version
                  </p>
                  <p className="font-medium">v{template.version}</p>
                </div>
              </CardContent>
              <CardFooter className="pt-4 border-t bg-muted/20 flex justify-between gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  className="gap-2 flex-1"
                  onClick={() => router.push(`/prompt-templates/${template.id}`)}
                >
                  <Edit className="h-4 w-4" /> Edit
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  className="gap-2 flex-1"
                  onClick={() => router.push(`/prompt-templates/new?duplicate=${template.id}`)}
                >
                  <Copy className="h-4 w-4" /> Clone
                </Button>
                <Button 
                  variant="destructive" 
                  size="sm"
                  className="px-3"
                  onClick={() => handleDelete(template.id)}
                  disabled={template.is_default}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </PageShell>
  );
}
