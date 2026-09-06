"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

interface UISignal {
  id: string;
  topic: string;
  score: string;
  source: string;
  trend: 'up' | 'down' | 'flat';
}

interface DownloadReportButtonProps {
  name: string;
  totalSignals: number;
  activeClusters: number;
  dataAnalyzed: string;
  activeReviewers: number;
  signals: UISignal[];
}

export default function DownloadReportButton({
  name,
  totalSignals,
  activeClusters,
  dataAnalyzed,
  activeReviewers,
  signals
}: DownloadReportButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDownload = () => {
    setIsGenerating(true);

    try {
      const doc = new jsPDF();
      
      // Title
      doc.setFontSize(22);
      doc.setTextColor(40);
      doc.text(`SignalForge Report: ${name}`, 14, 22);

      // Date
      doc.setFontSize(11);
      doc.setTextColor(100);
      doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 30);

      // Metrics Summary
      doc.setFontSize(14);
      doc.setTextColor(40);
      doc.text("Community Metrics Overview", 14, 45);

      doc.setFontSize(11);
      doc.setTextColor(80);
      doc.text(`Total Signals: ${totalSignals.toLocaleString()}`, 14, 53);
      doc.text(`Active Clusters: ${activeClusters}`, 14, 60);
      doc.text(`Data Analyzed: ${dataAnalyzed} GB`, 14, 67);
      doc.text(`Active Reviewers: ${activeReviewers}`, 14, 74);

      // Recent Signals Table
      doc.setFontSize(14);
      doc.setTextColor(40);
      doc.text("Recent Signals", 14, 90);

      const tableData = signals.map(s => [
        s.id.substring(0, 6),
        s.topic,
        s.source,
        s.score,
        s.trend === 'up' ? 'Rising' : s.trend === 'down' ? 'Falling' : 'Stable'
      ]);

      autoTable(doc, {
        startY: 95,
        head: [['ID', 'Signal Name', 'Source', 'Severity', 'Status']],
        body: tableData,
        theme: 'striped',
        headStyles: { fillColor: [24, 24, 27] }, // zinc-900 color
      });

      // Save the PDF
      const filename = `${name.replace(/\s+/g, '_')}_Overview_Report.pdf`;
      doc.save(filename);
    } catch (error) {
      console.error("Failed to generate PDF", error);
      alert("Failed to generate PDF report.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <button 
      onClick={handleDownload}
      disabled={isGenerating}
      className="bg-white text-black hover:bg-zinc-200 transition-colors px-6 py-2.5 rounded-md font-semibold text-sm flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
    >
      {isGenerating ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <Download className="w-4 h-4" />
      )}
      {isGenerating ? "Generating..." : "Download Report"}
    </button>
  );
}
