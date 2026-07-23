"use client";

import { useEffect, useState } from "react";
import { Loader2, ServerCrash, Trash2, FileText } from "lucide-react";
import { UploadDocumentModal } from "./upload-document-modal";
import { useToast } from "@/hooks/use-toast";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageShell } from "@/components/page-shell";

type Document = {
  id: string;
  world_id: string;
  filename: string;
  document_type?: string;
  department?: string;
  created_at: string;
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/documents");
      if (!res.ok) {
        throw new Error("Failed to fetch documents");
      }
      const data = await res.json();
      setDocuments(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const deleteDocument = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/documents/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        throw new Error("Failed to delete document");
      }
      toast({
        title: "Deleted",
        description: "The document has been deleted.",
      });
      fetchDocuments();
    } catch {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to delete document.",
      });
    }
  };

  return (
    <PageShell
      label="Documents"
      title="Documents"
      description="Enterprise knowledge base, files, and dataset resources."
    >
      <div className="flex items-center justify-end mb-6 mt-[-60px] relative z-10">
        <UploadDocumentModal onSuccess={fetchDocuments} />
      </div>

      {isLoading ? (
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading documents</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={fetchDocuments} variant="outline">
            Try again
          </Button>
        </div>
      ) : documents.length === 0 ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 rounded-lg border border-dashed text-center">
          <FileText className="h-12 w-12 text-muted-foreground" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">No documents found</h3>
            <p className="text-sm text-muted-foreground">
              Add a new enterprise document to get started.
            </p>
          </div>
          <UploadDocumentModal onSuccess={fetchDocuments} />
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Added</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell className="font-medium truncate max-w-[200px]" title={doc.filename}>
                    {doc.filename}
                  </TableCell>
                  <TableCell>
                    {doc.document_type ? (
                      <Badge variant="outline" className="uppercase">{doc.document_type}</Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {doc.department ? doc.department : <span className="text-muted-foreground">-</span>}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:bg-destructive/10"
                      onClick={() => deleteDocument(doc.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </PageShell>
  );
}
