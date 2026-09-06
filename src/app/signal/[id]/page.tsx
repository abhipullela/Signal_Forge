import { ArrowLeft, ExternalLink, Calendar, Database, Target, Network } from "lucide-react";
import Link from "next/link";
import { fetchSignalDetails } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default async function SignalDetail({ params }: { params: { id: string } }) {
  const signal = await fetchSignalDetails(params.id);

  if (!signal) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-6">
        <h1 className="text-2xl font-semibold mb-4">Signal Not Found</h1>
        <p className="text-zinc-400 mb-8">The requested signal could not be found or has been removed.</p>
        <Link 
          href="/" 
          className="bg-zinc-900 hover:bg-zinc-800 text-white px-6 py-2 rounded-md transition-colors font-medium flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const scoreLabel = ((signal.signal_score || 0) / 100).toFixed(1) + "x strength";
  const dateStr = signal.published_at ? new Date(signal.published_at).toLocaleString() : "Unknown Date";

  let communityName = "Unknown Community";
  if (signal.community_id === 423) communityName = "Datasets";
  else if (signal.community_id === 424) communityName = "Technology";
  else if (signal.community_id === 425) communityName = "Gaming";

  return (
    <div className="min-h-screen bg-background text-foreground p-6 md:p-12 font-sans relative overflow-hidden transition-colors duration-300">
      {/* Ambient Glow */}
      <div className="absolute top-[-150px] left-[-150px] w-[500px] h-[500px] bg-emerald-900/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-4xl mx-auto space-y-8 relative z-10">
        
        {/* Navigation & Header */}
        <div>
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6 transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground leading-tight">
              {signal.title || "Untitled Signal"}
            </h1>
            <Badge className="w-max bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 px-3 py-1 text-sm font-semibold uppercase tracking-wider">
              {signal.signal_status || "ACTIVE"}
            </Badge>
          </div>
        </div>

        {/* Metadata Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-card border-border backdrop-blur-xl p-4 flex flex-col gap-1 transition-colors duration-300">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Network className="w-4 h-4" />
              <span className="text-xs font-semibold uppercase tracking-wider">Score</span>
            </div>
            <span className="text-lg font-bold text-foreground">{scoreLabel}</span>
          </Card>

          <Card className="bg-card border-border backdrop-blur-xl p-4 flex flex-col gap-1 transition-colors duration-300">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Database className="w-4 h-4" />
              <span className="text-xs font-semibold uppercase tracking-wider">Community</span>
            </div>
            <span className="text-lg font-bold text-foreground">{communityName}</span>
          </Card>

          <Card className="bg-card border-border backdrop-blur-xl p-4 flex flex-col gap-1 transition-colors duration-300">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Target className="w-4 h-4" />
              <span className="text-xs font-semibold uppercase tracking-wider">Cluster ID</span>
            </div>
            <span className="text-lg font-bold text-foreground">{signal.cluster_id || "None"}</span>
          </Card>

          <Card className="bg-card border-border backdrop-blur-xl p-4 flex flex-col gap-1 transition-colors duration-300">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Calendar className="w-4 h-4" />
              <span className="text-xs font-semibold uppercase tracking-wider">Date</span>
            </div>
            <span className="text-sm font-medium text-muted-foreground mt-1">{dateStr}</span>
          </Card>
        </div>

        {/* Content Section */}
        <Card className="bg-card border-border overflow-hidden transition-colors duration-300">
          <div className="p-6 md:p-8 border-b border-border flex justify-between items-center">
            <h2 className="text-lg font-semibold text-foreground">Source Content</h2>
            {signal.url && signal.url !== "NaN" && (
              <a 
                href={signal.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-emerald-500 hover:text-emerald-400 transition-colors"
              >
                View Original <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
          <div className="p-6 md:p-8 bg-muted/20">
            <p className="text-foreground leading-relaxed whitespace-pre-wrap font-mono text-sm">
              {signal.content || "No detailed content available for this signal."}
            </p>
          </div>
        </Card>

      </div>
    </div>
  );
}
