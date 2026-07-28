"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { PageShell } from "@/components/page-shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Save, ArrowLeft, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

type PromptTemplate = {
  id?: string;
  name: string;
  description: string;
  system_prompt: string;
  user_prompt_template: string;
  version: number;
  is_default: boolean;
};

type PromptEditorProps = {
  templateId?: string;
  duplicateId?: string;
};

export function PromptEditor({ templateId, duplicateId }: PromptEditorProps) {
  const router = useRouter();
  const isEditing = !!templateId;
  const isDuplicating = !!duplicateId;

  const [formData, setFormData] = useState<PromptTemplate>({
    name: "",
    description: "",
    system_prompt: "",
    user_prompt_template: "",
    version: 1,
    is_default: false,
  });

  const [isLoading, setIsLoading] = useState(isEditing || isDuplicating);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTemplate = async (id: string) => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/prompt-templates/${id}`);
        if (!res.ok) throw new Error("Failed to load prompt template");
        const data = await res.json();

        if (isDuplicating) {
          setFormData({
            ...data,
            id: undefined,
            name: `${data.name} (Copy)`,
            version: data.version + 1,
            is_default: false,
          });
        } else {
          setFormData(data);
        }
      } catch (err: unknown) {
        if (err instanceof Error) setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    if (templateId) {
      fetchTemplate(templateId);
    } else if (duplicateId) {
      fetchTemplate(duplicateId);
    } else {
      setIsLoading(false);
    }
  }, [templateId, duplicateId, isDuplicating]);

  const handleChange = (field: keyof PromptTemplate, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const validateTemplate = () => {
    if (!formData.name.trim()) return "Name is required.";
    if (!formData.user_prompt_template.trim()) return "User Prompt is required.";

    // Check if required variables are present
    const reqVars = ["{{task_title}}", "{{task_description}}", "{{retrieved_context}}"];
    const missing = reqVars.filter(v => !formData.user_prompt_template.includes(v));

    if (missing.length > 0) {
      return `Warning: The following variables are missing: ${missing.join(', ')}. While not strictly required, they are highly recommended for AgentOps.`;
    }

    return null;
  };

  const handleSave = async () => {
    const validationWarning = validateTemplate();
    if (validationWarning && validationWarning.startsWith("Name") || validationWarning?.startsWith("User")) {
      setError(validationWarning);
      return;
    }

    // We can proceed even with warnings about variables, but let's prompt the user if we wanted to be strict.
    // For simplicity, we just save.

    setIsSaving(true);
    setError(null);

    try {
      const url = isEditing
        ? `http://localhost:8000/api/v1/prompt-templates/${templateId}`
        : `http://localhost:8000/api/v1/prompt-templates`;

      const method = isEditing ? "PUT" : "POST";

      const payload = {
        name: formData.name,
        description: formData.description || null,
        system_prompt: formData.system_prompt || null,
        user_prompt_template: formData.user_prompt_template,
        version: formData.version,
        is_default: formData.is_default
      };

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to save prompt template");
      }

      router.push("/prompt-templates");
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setIsSaving(false);
    }
  };

  const pageTitle = isEditing ? "Edit Prompt" : isDuplicating ? "Clone Prompt" : "Create Prompt";

  if (isLoading) {
    return (
      <PageShell label="Prompt Editor" title={pageTitle} description="Loading template details...">
        <div className="flex h-[400px] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-r-transparent" />
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell label="Prompt Editor" title={pageTitle} description="Define the system and user prompts used to evaluate your models.">
      <div className="mb-6 flex justify-between items-center">
        <Button variant="outline" onClick={() => router.push("/prompt-templates")} className="gap-2">
          <ArrowLeft className="h-4 w-4" /> Back to Library
        </Button>
        <Button onClick={handleSave} disabled={isSaving} className="gap-2">
          <Save className="h-4 w-4" /> {isSaving ? "Saving..." : "Save Template"}
        </Button>
      </div>

      {error && (
        <div className="mb-6 flex items-center gap-2 rounded-lg bg-destructive/10 p-4 text-destructive">
          <AlertCircle className="h-5 w-5" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>System Prompt</CardTitle>
              <CardDescription>Instructions that set the behavior and persona of the AI assistant.</CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="You are an enterprise AI assistant..."
                className="min-h-[120px] font-mono text-sm"
                value={formData.system_prompt}
                onChange={(e) => handleChange("system_prompt", e.target.value)}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>User Prompt Template</CardTitle>
              <CardDescription>
                The main template with variables injected at evaluation time.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2 mb-2">
                <Badge variant="outline" className="font-mono text-xs cursor-pointer hover:bg-accent" onClick={() => handleChange('user_prompt_template', formData.user_prompt_template + '{{task_title}}')}>{"{{task_title}}"}</Badge>
                <Badge variant="outline" className="font-mono text-xs cursor-pointer hover:bg-accent" onClick={() => handleChange('user_prompt_template', formData.user_prompt_template + '{{task_description}}')}>{"{{task_description}}"}</Badge>
                <Badge variant="outline" className="font-mono text-xs cursor-pointer hover:bg-accent" onClick={() => handleChange('user_prompt_template', formData.user_prompt_template + '{{retrieved_context}}')}>{"{{retrieved_context}}"}</Badge>
              </div>
              <Textarea
                placeholder="Task: {{task_title}}..."
                className="min-h-[400px] font-mono text-sm leading-relaxed"
                value={formData.user_prompt_template}
                onChange={(e) => handleChange("user_prompt_template", e.target.value)}
                required
              />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Template Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleChange("name", e.target.value)}
                  placeholder="e.g. Standard RAG v2"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="version">Version</Label>
                <Input
                  id="version"
                  type="number"
                  min="1"
                  value={formData.version}
                  onChange={(e) => handleChange("version", parseInt(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleChange("description", e.target.value)}
                  placeholder="What makes this prompt unique?"
                  className="min-h-[100px]"
                />
              </div>
              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="is_default"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={formData.is_default}
                  onChange={(e) => handleChange("is_default", e.target.checked)}
                />
                <Label htmlFor="is_default" className="font-medium">
                  Set as Default Template
                </Label>
              </div>
              <p className="text-xs text-muted-foreground pl-6">
                Experiments will use this template if none is specified.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageShell>
  );
}
