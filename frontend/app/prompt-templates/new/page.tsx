"use client";

import { useSearchParams } from "next/navigation";
import { PromptEditor } from "@/components/prompt-templates/PromptEditor";
import { Suspense } from "react";

function NewPromptContent() {
  const searchParams = useSearchParams();
  const duplicateId = searchParams.get("duplicate");

  return <PromptEditor duplicateId={duplicateId || undefined} />;
}

export default function NewPromptPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center">Loading editor...</div>}>
      <NewPromptContent />
    </Suspense>
  );
}
