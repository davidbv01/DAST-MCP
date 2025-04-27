
import { useState } from "react";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "@/hooks/use-toast";
import DastForm from "@/components/DastForm";
import BrowserPreview from "@/components/BrowserPreview";
import AiMessagePanel from "@/components/AiMessagePanel";
import ScanProgress from "@/components/ScanProgress";
import ReportGenerator from "@/components/ReportGenerator";

const Index = () => {
  const [scanning, setScanning] = useState(false);
  const [scanComplete, setScanComplete] = useState(false);
  const [targetUrl, setTargetUrl] = useState("");
  
  const handleStartScan = (data: {
    url: string;
    email: string;
    username: string;
    password: string;
  }) => {
    // Reset previous scan state
    setScanComplete(false);
    
    // Set the target URL for display
    setTargetUrl(data.url);
    
    // Start the scan process
    setScanning(true);
    
    // Display notification
    toast({
      title: "Scan Started",
      description: `Starting DAST scan for ${data.url}`,
    });
  };
  
  const handleScanComplete = () => {
    setScanComplete(true);
    setScanning(false);
    
    toast({
      title: "Scan Complete",
      description: "DAST scan has completed successfully!",
    });
  };
  
  return (
    <div className="min-h-screen bg-background">
      <Toaster />
      <div className="container py-8 px-4 mx-auto">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Web Security DAST Scanner</h1>
          <p className="text-muted-foreground">
            Find security vulnerabilities in web applications with dynamic scanning
          </p>
        </header>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column - Form and Report */}
          <div className="space-y-6">
            <DastForm onSubmit={handleStartScan} />
            <ReportGenerator isComplete={scanComplete} url={targetUrl} />
          </div>
          
          {/* Middle column - Browser Preview */}
          <div className="lg:col-span-2">
            <BrowserPreview active={scanning || scanComplete} url={targetUrl} />
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Bottom row - Progress and AI Messages */}
          <ScanProgress isScanning={scanning} onComplete={handleScanComplete} />
          <AiMessagePanel isScanning={scanning || scanComplete} />
        </div>
      </div>
    </div>
  );
};

export default Index;
