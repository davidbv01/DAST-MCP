
import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Message {
  content: string;
  type: "info" | "warning" | "error" | "success";
}

interface AiMessagePanelProps {
  isScanning: boolean;
}

export default function AiMessagePanel({ isScanning }: AiMessagePanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  useEffect(() => {
    if (isScanning) {
      const initialMessages = [
        {
          content: "Starting DAST scan. Initializing scanner...",
          type: "info" as const
        }
      ];
      
      setMessages(initialMessages);
      
      const scanMessages = [
        { 
          content: "Crawling site structure to identify endpoints.",
          type: "info" as const 
        },
        { 
          content: "Testing authentication mechanism.",
          type: "info" as const 
        },
        { 
          content: "Authentication successful. Proceeding with scan.",
          type: "success" as const 
        },
        { 
          content: "Testing for XSS vulnerabilities in inputs.",
          type: "info" as const 
        },
        { 
          content: "Warning: Potential XSS vulnerability found in search form.",
          type: "warning" as const 
        },
        { 
          content: "Testing for SQL injection.",
          type: "info" as const 
        },
        { 
          content: "Testing for CSRF vulnerabilities.",
          type: "info" as const 
        },
        { 
          content: "Warning: Missing CSRF tokens in form submission.",
          type: "warning" as const 
        },
        { 
          content: "Analyzing HTTP security headers.",
          type: "info" as const 
        },
        { 
          content: "Error: Missing Content-Security-Policy header.",
          type: "error" as const 
        },
        { 
          content: "Testing for sensitive data exposure.",
          type: "info" as const 
        },
        { 
          content: "Testing for misconfigured access controls.",
          type: "info" as const 
        },
        { 
          content: "Scan completed. Generating report with 2 critical, 3 high, and 5 medium risks identified.",
          type: "success" as const 
        }
      ];
      
      let messageIndex = 0;
      
      const interval = setInterval(() => {
        if (messageIndex < scanMessages.length) {
          setMessages(prev => [...prev, scanMessages[messageIndex]]);
          messageIndex++;
        } else {
          clearInterval(interval);
        }
      }, 3000);
      
      return () => clearInterval(interval);
    } else {
      setMessages([]);
    }
  }, [isScanning]);
  
  const getMessageClass = (type: Message["type"]) => {
    switch (type) {
      case "info":
        return "text-blue-600 dark:text-blue-400";
      case "warning":
        return "text-amber-600 dark:text-amber-400";
      case "error":
        return "text-destructive";
      case "success":
        return "text-emerald-600 dark:text-emerald-400";
      default:
        return "";
    }
  };
  
  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">AI Assistant Messages</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] overflow-auto border rounded-md p-3 bg-secondary/30 space-y-2">
          {messages.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              AI messages will appear here during the scan
            </p>
          ) : (
            messages.map((message, index) => (
              <div key={index} className="text-sm">
                <span className={getMessageClass(message.type)}>
                  {message.content}
                </span>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </CardContent>
    </Card>
  );
}
