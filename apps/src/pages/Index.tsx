import { useState, useEffect } from "react";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "@/hooks/use-toast";
import DastForm from "@/components/DastForm";
import BrowserPreview from "@/components/BrowserPreview";
import ReportGenerator from "@/components/ReportGenerator";

const Index = () => {
  const [scanStatus, setScanStatus] = useState({
    scanning: false,
    scanComplete: false,
  });
  const [targetUrl, setTargetUrl] = useState("");
  const [logs, setLogs] = useState<string>(""); // State to store logs as plain text
  const [isScrapingFinished, setIsScrapingFinished] = useState(false); // State to check if scraping is finished
  const [screenshot, setScreenshot] = useState<string | null>(null); // State to store the screenshot
  const [isLatitudeEnable, setIsLatitudeEnable] = useState(true); // Variable to track if latitude (screenshot) is enabled
  const [htmlReport, setHtmlReport] = useState<string | null>(null);

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
          if (isLatitudeEnable) {
            const screenshotResponse = await fetch("http://localhost:8000/screenshot");
            if (screenshotResponse.ok) {
              const contentType = screenshotResponse.headers.get("Content-Type");
              if (contentType && contentType.includes("application/json")) {
                const data = await screenshotResponse.json();
                if (data.message?.includes("Scraping finished")) {
                  console.log("Scraping finished. Switching to log mode.");
                  setIsLatitudeEnable(false);
  
                  const logsResponse = await fetch("http://localhost:8000/logs");
                  if (logsResponse.ok) {
                    const logsText = await logsResponse.text();
                    setLogs(logsText);
                    setIsScrapingFinished(true); 
                  }
                }
              } else {
                const screenshotBlob = await screenshotResponse.blob();
                const screenshotUrl = URL.createObjectURL(screenshotBlob);
                setScreenshot(screenshotUrl);
              }
            } else {
              console.error("Failed to fetch screenshot");
            }
          } else {  
            if (!isScrapingFinished) {
              const logsResponse = await fetch("http://localhost:8000/logs");
              if (logsResponse.ok) {
                const logsText = await logsResponse.text();
                setLogs(logsText);
                setIsScrapingFinished(true);
              }
            }
          }
        } catch (error) {
          console.error("Error fetching screenshot or logs:", error);
        }
      }, 2000);
  
      return () => clearInterval(intervalId);
    }
  }, [scanStatus.scanning, isLatitudeEnable, isScrapingFinished]);
  

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
            <ReportGenerator isComplete={scanStatus.scanComplete} url={targetUrl}  onReportReady={(html: string) => setHtmlReport(html)} />
          </div>

          {/* Middle column - Browser Preview */}
          <div className="lg:col-span-2">
            <BrowserPreview
              active={scanStatus.scanning || scanStatus.scanComplete}
              url={targetUrl}
              logs={logs}
              isScrapingFinished={isScrapingFinished}
              isLatitudeEnable={isLatitudeEnable}
              screenshot={screenshot}
              htmlReport={htmlReport}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
