
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";

interface ReportGeneratorProps {
  isComplete: boolean;
  url: string;
}

export default function ReportGenerator({ isComplete, url }: ReportGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  
  const handleGenerateReport = () => {
    if (!isComplete) return;
    
    setIsGenerating(true);
    
    // Simulate PDF generation
    setTimeout(() => {
      setIsGenerating(false);
      
      toast({
        title: "PDF Report Generated",
        description: "Your security report has been prepared and is ready to download.",
      });
    }, 3000);
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
              {isGenerating ? "Generating PDF..." : "Generate PDF Report"}
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
