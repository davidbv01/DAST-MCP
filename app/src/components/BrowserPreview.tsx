
import { useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";

interface BrowserPreviewProps {
  active: boolean;
  url: string;
}

export default function BrowserPreview({ active, url }: BrowserPreviewProps) {
  const browserRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (active && browserRef.current) {
      // Simulate browser interactions
      const actions = [
        "Loading page...",
        "Inspecting DOM structure...",
        "Analyzing form elements...",
        "Testing input fields...",
        "Checking for XSS vulnerabilities...",
        "Testing for SQL injection...",
        "Analyzing response headers...",
        "Checking security headers...",
        "Testing for CSRF vulnerabilities...",
        "Reviewing cookie security..."
      ];
      
      let i = 0;
      const interval = setInterval(() => {
        if (browserRef.current) {
          if (i < actions.length) {
            const actionEl = document.createElement("div");
            actionEl.className = "text-xs text-muted-foreground my-1";
            actionEl.textContent = `> ${actions[i]}`;
            browserRef.current.appendChild(actionEl);
            
            // Auto scroll to bottom
            browserRef.current.scrollTop = browserRef.current.scrollHeight;
            i++;
          } else {
            clearInterval(interval);
          }
        }
      }, 2000);
      
      return () => clearInterval(interval);
    }
  }, [active]);
  
  if (!active) {
    return (
      <Card className="w-full h-[350px] flex items-center justify-center bg-secondary/50">
        <p className="text-muted-foreground">Browser preview will appear here</p>
      </Card>
    );
  }
  
  return (
    <Card className="w-full">
      <div className="bg-secondary flex items-center px-4 py-2 border-b">
        <div className="flex space-x-1.5 mr-4">
          <div className="w-3 h-3 rounded-full bg-destructive opacity-70"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500 opacity-70"></div>
          <div className="w-3 h-3 rounded-full bg-green-500 opacity-70"></div>
        </div>
        <div className="bg-background flex-1 px-3 py-1 rounded text-sm truncate">
          {url}
        </div>
      </div>
      <CardContent className="p-0">
        <div className="bg-card border-t-0 h-[300px] overflow-auto p-4" ref={browserRef}>
          <div className="text-xs text-muted-foreground my-1">
            Initializing browser session...
          </div>
          <div className="text-xs text-muted-foreground my-1">
            Navigating to {url}...
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
