import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";

interface BrowserPreviewProps {
  active: boolean;
  url: string;
}

export default function BrowserPreview({ active, url }: BrowserPreviewProps) {
  const [logs, setLogs] = useState<string[]>([]); // Estado para almacenar los logs
  const [isScrapingFinished, setIsScrapingFinished] = useState(false); // Estado para saber si ha terminado el scraping

  useEffect(() => {
    if (active) {
      const fetchLogs = async () => {
        try {
          const response = await fetch("http://localhost:8000/logs"); // Cambia la URL según tu servidor
          if (response.ok) {
            const logData = await response.json(); // Suponemos que la respuesta es un JSON
            setLogs(logData.logs); // Guarda los logs en el estado
          } else {
            console.error("Failed to fetch logs");
          }
        } catch (error) {
          console.error("Error fetching logs:", error);
        }
      };

      // Configura un intervalo para actualizar los logs periódicamente (cada 1 segundo)
      const intervalId = setInterval(() => {
        fetchLogs();
      }, 1000);

      // Limpia el intervalo cuando el componente se desactive o termine el scraping
      return () => clearInterval(intervalId);
    }
  }, [active]);

  useEffect(() => {
    // Esta función se puede llamar cuando el scraping termina en el backend
    // Aquí asumimos que hay alguna lógica que determina cuándo terminó el scraping
    if (isScrapingFinished) {
      // Cuando el scraping haya terminado, comienza a mostrar los logs en vez de la captura
      setLogs(["Scraping finished. Now starting the ZAP scan..."]); // Mostrar mensaje de inicio de ZAP
    }
  }, [isScrapingFinished]);

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
        <div className="bg-card border-t-0 h-[650px] overflow-auto p-4">
          {/* Mostrar los logs si están disponibles */}
          {!isScrapingFinished ? (
            <div className="text-xs text-muted-foreground my-1">Loading logs...</div>
          ) : (
            <div className="text-xs text-muted-foreground my-1">
              {logs.length > 0 ? (
                logs.map((log, index) => <div key={index}>{log}</div>)
              ) : (
                <p>No logs available.</p>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
