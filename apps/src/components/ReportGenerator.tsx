import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";

interface ReportGeneratorProps {
  isComplete: boolean;
  url: string;
  onReportReady: (html: string) => void;
}

export default function ReportGenerator({ isComplete, url, onReportReady }: ReportGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateReport = async () => {
    if (!isComplete) return;
    setIsGenerating(true);

    try {
      const response = await fetch("http://localhost:8000/report"); // Cambia el puerto si es necesario
      if (!response.ok) throw new Error("Error fetching report");

      const html = await response.text();
      onReportReady(html); // Pasar HTML al componente padre

      toast({
        title: "HTML Report Generated",
        description: "Your security report is ready and passed to the parent component.",
      });
    } catch (error) {
      toast({
        title: "Failed to generate report",
        description: "Could not fetch the report from the server.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const scanDate = new Date().toLocaleDateString();

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Security Report</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isComplete ? (
          <>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Target URL:</span>
                <span className="font-medium truncate max-w-[200px]">{url}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Scan Date:</span>
                <span className="font-medium">{scanDate}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Issues Found:</span>
                <span className="font-medium">10 (2 Critical)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Overall Risk:</span>
                <span className="font-medium text-amber-500">Medium</span>
              </div>
            </div>

            <Button
              className="w-full"
              onClick={handleGenerateReport}
              disabled={isGenerating}
            >
              {isGenerating ? "Fetching HTML..." : "Generate HTML Report"}
            </Button>
          </>
        ) : (
          <div className="py-6 text-center text-muted-foreground">
            Complete the scan to generate a security report
          </div>
        )}
      </CardContent>
    </Card>
  );
}
