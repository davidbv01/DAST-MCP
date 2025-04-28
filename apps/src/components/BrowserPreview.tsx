import { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";

interface BrowserPreviewProps {
  active: boolean;
  url: string;
}

export default function BrowserPreview({ active, url }: BrowserPreviewProps) {
  const [screenshot, setScreenshot] = useState<string | null>(null); // Estado para almacenar la imagen

  useEffect(() => {
    if (active) {
      const fetchScreenshot = async () => {
        try {
          const response = await fetch("http://localhost:8000/screenshot"); // Cambia la URL según tu servidor
          if (response.ok) {
            const blob = await response.blob(); // Convierte la respuesta en un blob
            const imageUrl = URL.createObjectURL(blob); // Crea un URL temporal para la imagen
            setScreenshot(imageUrl); // Guarda la URL en el estado
          } else {
            console.error("Failed to fetch screenshot");
          }
        } catch (error) {
          console.error("Error fetching screenshot:", error);
        }
      };

      // Inicializa la captura de pantalla al activar el componente
      fetchScreenshot();

      // Configura un intervalo para actualizar la captura de pantalla periódicamente (cada 5 segundos)
      const intervalId = setInterval(() => {
        fetchScreenshot();
      }, 2000); // 5000ms = 5 segundos

      // Limpia el intervalo cuando el componente se desactive
      return () => clearInterval(intervalId);
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
        <div className="bg-card border-t-0 h-[650px] overflow-auto p-4">
          {/* Render the screenshot if available */}
          {screenshot ? (
            <img src={screenshot} alt="Browser Screenshot" className="w-full h-auto" />
          ) : (
            <div className="text-xs text-muted-foreground my-1">
              Loading screenshot...
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
