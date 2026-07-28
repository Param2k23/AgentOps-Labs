"use client";

import { PromptEditor } from "@/components/prompt-templates/PromptEditor";

export default function EditPromptPage({ params }: { params: { id: string } }) {
  return <PromptEditor templateId={params.id} />;
}
