import { Card, CardContent } from "@/components/ui/card";

interface BrowserPreviewProps {
  active: boolean;
  url: string;
  logs: string;
  isScrapingFinished: boolean;
  isLatitudeEnable: boolean;
  screenshot: string | null;
}

export default function BrowserPreview({
  active,
  url,
  logs,
  isScrapingFinished,
  isLatitudeEnable,
  screenshot,
}: BrowserPreviewProps) {
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
          {/* Show screenshot while scraping is enabled */}
          {isLatitudeEnable && screenshot ? (
            <div className="my-2">
              <img src={screenshot} alt="Screenshot" className="w-full h-auto" />
            </div>
          ) : (
            <div className="text-xs text-muted-foreground my-1">Loading screenshot...</div>
          )}

          {/* Show logs once scraping is finished */}
          {isScrapingFinished ? (
            <div className="text-xs text-muted-foreground my-1">
              {logs.length > 0 ? (
                <pre>{logs}</pre>
              ) : (
                <p>No logs available.</p>
              )}
            </div>
          ) : (
            <div className="text-xs text-muted-foreground my-1">Loading logs...</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}