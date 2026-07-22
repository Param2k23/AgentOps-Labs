"use client";

import { useEffect, useState } from "react";
import { Loader2, ServerCrash, Trash2, Globe } from "lucide-react";
import { CreateWorldModal } from "./create-world-modal";
import { useToast } from "@/hooks/use-toast";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageShell } from "@/components/page-shell";

type World = {
  id: string;
  name: string;
  description?: string;
  industry?: string;
  status: string;
  created_at: string;
};

export default function WorldsPage() {
  const [worlds, setWorlds] = useState<World[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchWorlds = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/worlds");
      if (!res.ok) {
        throw new Error("Failed to fetch worlds");
      }
      const data = await res.json();
      setWorlds(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWorlds();
  }, []);

  const deleteWorld = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/worlds/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        throw new Error("Failed to delete world");
      }
      toast({
        title: "Deleted",
        description: "The world has been deleted.",
      });
      fetchWorlds();
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to delete world.",
      });
    }
  };

  return (
    <PageShell
      label="Worlds"
      title="Worlds"
      description="Enterprise environments, datasets, and simulated organizations."
    >
      <div className="flex items-center justify-end mb-6 mt-[-60px] relative z-10">
        <CreateWorldModal onSuccess={fetchWorlds} />
      </div>

      {isLoading ? (
        <div className="flex h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 text-center">
          <ServerCrash className="h-12 w-12 text-destructive" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Error loading worlds</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={fetchWorlds} variant="outline">
            Try again
          </Button>
        </div>
      ) : worlds.length === 0 ? (
        <div className="flex h-[400px] flex-col items-center justify-center space-y-4 rounded-lg border border-dashed text-center">
          <Globe className="h-12 w-12 text-muted-foreground" />
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">No worlds created</h3>
            <p className="text-sm text-muted-foreground">
              Create a new enterprise world environment to get started.
            </p>
          </div>
          <CreateWorldModal onSuccess={fetchWorlds} />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {worlds.map((world) => (
            <Card key={world.id} className="flex flex-col">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-xl font-bold truncate pr-4">
                  {world.name}
                </CardTitle>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-destructive hover:bg-destructive/10 shrink-0"
                  onClick={() => deleteWorld(world.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent className="flex-1">
                <div className="space-y-2 h-full flex flex-col">
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {world.description || "No description provided."}
                  </p>
                  <div className="flex flex-wrap gap-2 pt-4 mt-auto">
                    {world.industry && (
                      <Badge variant="secondary">{world.industry}</Badge>
                    )}
                    <Badge variant={world.status === "active" ? "default" : "secondary"}>
                      {world.status}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </PageShell>
  );
}
