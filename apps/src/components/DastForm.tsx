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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Handle Submit Start');
    onSubmit({ url, email, username, password });
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
      console.log('Handle Fetch Start');
      const response = await fetch('http://localhost:8000/start_latitude', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          username: username,
          password: password,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend Response:', data);
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

          {/* Siempre mostrar Username y Password */}
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
