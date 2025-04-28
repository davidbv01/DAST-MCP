import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield } from "lucide-react";

interface DastFormProps {
  onSubmit: (data: {
    url: string;
    email: string;
    username: string;
    password: string;
  }) => void;
}

export default function DastForm({ onSubmit }: DastFormProps) {
  const [url, setUrl] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showCredentials, setShowCredentials] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Llamar a la función onSubmit para manejar los datos del formulario
    onSubmit({
      url,
      email,
      username,
      password,
    });
    
    // Llamar a la función para hacer la petición GET
    launchScan();
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  };

  const isValidEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const isFormValid = url && isValidUrl(url) && email && isValidEmail(email);

  const launchScan = async () => {
    try {
      const response = await fetch('http://localhost:8000/scan', {
        method: 'GET', // O 'POST' si necesitas enviar los datos en el cuerpo de la solicitud
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          email,
          username,
          password
        }),
      });

      const data = await response.json();
      console.log('Backend Response:', data); // Mostrar la respuesta del backend
    } catch (error) {
      console.error('Error al lanzar el escaneo:', error);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="space-y-1">
        <div className="flex items-center space-x-2">
          <Shield className="h-6 w-6 text-primary" />
          <CardTitle className="text-2xl">DAST Scanner</CardTitle>
        </div>
        <CardDescription>
          Enter the URL to scan and your email to receive results
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="url">Target URL</Label>
            <Input
              id="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
            {url && !isValidUrl(url) && (
              <p className="text-sm text-destructive">Please enter a valid URL</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            {email && !isValidEmail(email) && (
              <p className="text-sm text-destructive">Please enter a valid email</p>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="credentials"
              checked={showCredentials}
              onChange={() => setShowCredentials(!showCredentials)}
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <Label htmlFor="credentials" className="text-sm">
              Target requires authentication
            </Label>
          </div>

          {showCredentials && (
            <div className="space-y-4 pt-2">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
          )}

          <Button 
            type="submit" 
            className="w-full" 
            disabled={!isFormValid}
          >
            Launch Scan
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
