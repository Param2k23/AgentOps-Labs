/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export function ComparisonTable({ runs, onRowClick }: { runs: any[], onRowClick: (id: string) => void }) {
  if (!runs || runs.length === 0) return null;

  return (
    <div className="rounded-xl border bg-card text-card-foreground shadow-sm">
      <div className="p-6">
        <h3 className="text-lg font-medium leading-none tracking-tight mb-4">Comparison Table</h3>
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model</TableHead>
                <TableHead>Prompt</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Overall</TableHead>
                <TableHead>Accuracy</TableHead>
                <TableHead>Groundedness</TableHead>
                <TableHead>Retrieval</TableHead>
                <TableHead>Hallucination</TableHead>
                <TableHead>Latency (ms)</TableHead>
                <TableHead>Total Tokens</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => (
                <TableRow 
                  key={run.id} 
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => onRowClick(run.id)}
                >
                  <TableCell className="font-medium whitespace-nowrap">{run.model_name}</TableCell>
                  <TableCell className="whitespace-nowrap text-muted-foreground text-xs">
                    {run.prompt_template_name ? (
                      <span title={`${run.prompt_template_name} v${run.prompt_template_version}`}>
                        {run.prompt_template_name} v{run.prompt_template_version}
                      </span>
                    ) : (
                      "Default"
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-1 items-start">
                      <Badge 
                        variant={
                          run.status === "completed" ? "default" : 
                          ["failed", "provider_error", "invalid_api_key"].includes(run.status) ? "destructive" : 
                          ["rate_limited", "timeout"].includes(run.status) ? "outline" : "secondary"
                        } 
                        className={`uppercase ${["rate_limited", "timeout"].includes(run.status) ? "border-orange-500 text-orange-500" : ""}`}
                      >
                        {run.status.replace("_", " ")}
                      </Badge>
                      {run.error_message && (
                        <span className="text-xs text-muted-foreground truncate max-w-[150px]" title={run.error_message}>
                          {run.error_message}
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{run.overall_score !== null ? run.overall_score : "-"}</TableCell>
                  <TableCell>{run.accuracy !== null ? run.accuracy : "-"}</TableCell>
                  <TableCell>{run.groundedness !== null ? run.groundedness : "-"}</TableCell>
                  <TableCell>{run.retrieval_score !== null ? run.retrieval_score : "-"}</TableCell>
                  <TableCell>{run.hallucination_score !== null ? run.hallucination_score : "-"}</TableCell>
                  <TableCell>{run.latency_ms !== null ? run.latency_ms : "-"}</TableCell>
                  <TableCell>{run.total_tokens !== null ? run.total_tokens : "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
