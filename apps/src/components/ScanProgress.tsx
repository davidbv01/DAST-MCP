
import { useEffect, useState } from "react";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ScanProgressProps {
  isScanning: boolean;
  onComplete: () => void;
}

export default function ScanProgress({ isScanning, onComplete }: ScanProgressProps) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("Waiting to start");
  
  useEffect(() => {
    if (!isScanning) {
      setProgress(0);
      setStatus("Waiting to start");
      return;
    }
    
    // Reset progress when starting a new scan
    setProgress(0);
    setStatus("Initializing scan...");
    
    const scanStages = [
      "Crawling website structure...",
      "Testing authentication...",
      "Scanning for XSS vulnerabilities...",
      "Testing SQL injection points...",
      "Checking for CSRF vulnerabilities...",
      "Analyzing HTTP security headers...",
      "Testing for sensitive data exposure...",
      "Checking access controls...",
      "Finalizing results...",
      "Generating report..."
    ];
    
    let stageIndex = 0;
    const totalDuration = 40000; // 40 seconds for full scan
    const interval = setInterval(() => {
      setProgress(prev => {
        // Calculate next progress
        const newProgress = prev + 100 / (totalDuration / 1000);
        
        // Update status message at certain progress points
        if (newProgress >= (stageIndex + 1) * 10 && stageIndex < scanStages.length) {
          setStatus(scanStages[stageIndex]);
          stageIndex++;
        }
        
        // Complete the scan
        if (newProgress >= 100) {
          clearInterval(interval);
          setStatus("Scan completed");
          onComplete();
          return 100;
        }
        
        return newProgress;
      });
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isScanning, onComplete]);
  
  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Scan Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={progress} className="h-2" />
        <div className="flex justify-between text-sm">
          <span className={isScanning ? "text-primary" : "text-muted-foreground"}>
            {status}
          </span>
          <span className="font-medium">{Math.round(progress)}%</span>
        </div>
      </CardContent>
    </Card>
  );
}
