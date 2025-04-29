import { useState, useEffect } from "react";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "@/hooks/use-toast";
import DastForm from "@/components/DastForm";
import BrowserPreview from "@/components/BrowserPreview";
import ScanProgress from "@/components/ScanProgress";
import ReportGenerator from "@/components/ReportGenerator";

const Index = () => {
  const [scanStatus, setScanStatus] = useState({
    scanning: false,
    scanComplete: false,
  });
  const [targetUrl, setTargetUrl] = useState("");
  const [logs, setLogs] = useState<string>(""); // State to store logs as plain text
  const [isScrapingFinished, setIsScrapingFinished] = useState(false); // State to check if scraping is finished

  const handleStartScan = async (data: {
    url: string;
    email: string;
    username: string;
    password: string;
  }) => {
    // Reset previous scan state
    setScanStatus({ scanning: true, scanComplete: false });
    setTargetUrl(data.url);
    
    // Display notification
    toast({
      title: "Scan Started",
      description: `Starting DAST scan for ${data.url}`,
    });

    try {
      const response = await fetch("http://localhost:8000/start_latitude", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: data.url,
          username: data.username,
          password: data.password,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const resData = await response.json();
      console.log("Backend Response:", resData);
    } catch (error) {
      console.error("Error al lanzar el escaneo:", error);
      setScanStatus({ scanning: false, scanComplete: false }); // rollback si falla
    }
  };

  useEffect(() => {
    if (scanStatus.scanning) {
      const intervalId = setInterval(async () => {
        try {
          const response = await fetch("http://localhost:8000/logs");
          if (response.ok) {
            const logData = await response.text();
            setLogs(logData);
            // Puedes analizar aquí si ha acabado el scraping
            if (logData.includes("Scraping finished")) {
              setIsScrapingFinished(true);
            }
          } else {
            console.error("Failed to fetch logs");
          }
        } catch (error) {
          console.error("Error fetching logs:", error);
        }
      }, 1000);

      return () => clearInterval(intervalId);
    }
  }, [scanStatus.scanning]);

  const handleScanComplete = () => {
    setScanStatus({ scanning: false, scanComplete: true });
    
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
            <DastForm onSubmit={handleStartScan} isScanning={scanStatus.scanning} />
            <ReportGenerator isComplete={scanStatus.scanComplete} url={targetUrl} />
          </div>
          
          {/* Middle column - Browser Preview */}
          <div className="lg:col-span-2">
            <BrowserPreview active={scanStatus.scanning || scanStatus.scanComplete} url={targetUrl} logs={logs} isScrapingFinished={isScrapingFinished}/>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Bottom row - Progress and AI Messages */}
          <ScanProgress isScanning={scanStatus.scanning} onComplete={handleScanComplete} />
        </div>
      </div>
    </div>
  );
};

export default Index;
