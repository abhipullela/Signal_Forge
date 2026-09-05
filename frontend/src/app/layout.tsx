import './globals.css'
import type { Metadata } from 'next'
import { Inter } from "next/font/google";
import { cn } from "@/lib/utils";
import Sidebar from "@/components/Sidebar";

const inter = Inter({subsets:['latin'],variable:'--font-sans'});

export const metadata: Metadata = {
  title: 'SignalForge',
  description: 'ML-based micro-trend detection platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={cn("font-sans", inter.variable)}>
      <body className="bg-black text-white antialiased">
        <Sidebar />
        <main className="ml-16 min-h-screen">
          {children}
        </main>
      </body>
    </html>
  )
}
