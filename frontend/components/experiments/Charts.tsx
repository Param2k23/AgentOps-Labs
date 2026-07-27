/* eslint-disable @typescript-eslint/no-explicit-any */
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Charts({ runs }: { runs: Record<string, any>[] }) {
  const completedRuns = runs.filter(r => r.status === "completed");
  
  if (completedRuns.length === 0) return null;
  
  // Format data
  const data = completedRuns.map(r => ({
    name: r.model_name?.replace("nvidia/", "").replace("google/", "").replace("cohere/", "").replace(":free", "") || "Unknown",
    overall: parseFloat(r.overall_score) || 0,
    accuracy: parseFloat(r.accuracy) || 0,
    groundedness: parseFloat(r.groundedness) || 0,
    latency: r.latency_ms || 0,
    tokens: r.total_tokens || 0
  }));

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Scores Comparison</CardTitle>
        </CardHeader>
        <CardContent className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{fontSize: 12}} interval={0} angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend verticalAlign="top" height={36} />
              <Bar dataKey="overall" name="Overall" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="accuracy" name="Accuracy" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="groundedness" name="Groundedness" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Latency vs Tokens</CardTitle>
        </CardHeader>
        <CardContent className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{fontSize: 12}} interval={0} angle={-45} textAnchor="end" height={80} />
              <YAxis yAxisId="left" orientation="left" stroke="#f59e0b" />
              <YAxis yAxisId="right" orientation="right" stroke="#64748b" />
              <Tooltip />
              <Legend verticalAlign="top" height={36} />
              <Bar yAxisId="left" dataKey="latency" name="Latency (ms)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="right" dataKey="tokens" name="Total Tokens" fill="#64748b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
