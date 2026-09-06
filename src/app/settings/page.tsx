"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Laptop, Settings as SettingsIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null; // Avoid hydration mismatch
  }

  return (
    <div className="p-8 max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center gap-3 mb-8">
        <SettingsIcon className="w-8 h-8 text-primary" />
        <h1 className="text-4xl font-bold tracking-tight">Settings</h1>
      </div>

      <div className="grid gap-8">
        <section>
          <h2 className="text-2xl font-semibold mb-4">Appearance</h2>
          <Card className="p-6 bg-card border-border backdrop-blur-xl transition-colors duration-300">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h3 className="font-medium text-lg">Theme Preference</h3>
                <p className="text-muted-foreground text-sm">
                  Customize the appearance of SignalForge. Select light, dark, or sync with your system.
                </p>
              </div>
              <div className="flex bg-muted/50 p-1 rounded-lg border border-border">
                <Button
                  variant="ghost"
                  className={cn(
                    "rounded-md px-4 py-2 transition-all",
                    theme === 'light' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                  )}
                  onClick={() => setTheme('light')}
                >
                  <Sun className="w-4 h-4 mr-2" />
                  Light
                </Button>
                <Button
                  variant="ghost"
                  className={cn(
                    "rounded-md px-4 py-2 transition-all",
                    theme === 'dark' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                  )}
                  onClick={() => setTheme('dark')}
                >
                  <Moon className="w-4 h-4 mr-2" />
                  Dark
                </Button>
                <Button
                  variant="ghost"
                  className={cn(
                    "rounded-md px-4 py-2 transition-all",
                    theme === 'system' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                  )}
                  onClick={() => setTheme('system')}
                >
                  <Laptop className="w-4 h-4 mr-2" />
                  System
                </Button>
              </div>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}
