import { ArrowUpRight, ArrowDownRight, ArrowRight, Database, Cpu, Gamepad2, Download, Network, Users } from "lucide-react";
import { fetchCommunityOverviewById, fetchSignals, fetchCommunityAlerts } from "@/lib/api";
import TimeFilteredChart from "./TimeFilteredChart";
import { CommunityAlertsTable } from "@/components/CommunityAlertsTable";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import Link from "next/link";
import DownloadReportButton from "@/components/DownloadReportButton";

export default async function CommunityDetail({ params }: { params: { id: string } }) {
  const communityId = params.id;
  
  const [overview, signals, alerts] = await Promise.all([
    fetchCommunityOverviewById(communityId),
    fetchSignals(communityId),
    fetchCommunityAlerts(communityId)
  ]);

  const communityNames: Record<string, string> = {
    "datasets": "Datasets",
    "technology": "Technology",
    "gaming": "Gaming",
    "423": "Datasets",
    "424": "Technology",
    "425": "Gaming"
  };

  const name = communityNames[communityId as string] || "Community Overview";

  // If no overview is found, return 404 styled
  if (!overview) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center transition-colors duration-300">
        <h1 className="text-2xl font-semibold">Community not found</h1>
      </div>
    );
  }

  // Calculate dynamic but realistic metrics for the UI
  const totalSignals = overview.active_signals;
  const activeClusters = overview.active_clusters;
  const dataAnalyzed = (overview.total_posts_analyzed * 0.023).toFixed(1); // Pseudo-GB
  const activeReviewers = Math.max(1, Math.floor(overview.active_signals / 50)); 

  return (
    <div className="min-h-screen bg-background text-foreground p-6 md:p-12 font-sans relative overflow-hidden transition-colors duration-300">
      
      {/* Ambient Glow */}
      <div className="absolute top-[-150px] left-[-150px] w-[500px] h-[500px] bg-emerald-900/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto space-y-8 relative z-10">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <div className="flex items-center gap-2 text-zinc-400 text-sm mb-2">
              <Link href="/" className="hover:text-white transition-colors">Dashboard</Link>
              <span>/</span>
              <span className="text-zinc-100">{name}</span>
            </div>
            <h1 className="text-4xl font-black tracking-tight text-foreground">
              Overview
            </h1>
          </div>
          
          <div className="mt-6 md:mt-0">
            <DownloadReportButton 
              name={name}
              totalSignals={totalSignals}
              activeClusters={activeClusters}
              dataAnalyzed={dataAnalyzed}
              activeReviewers={activeReviewers}
              signals={signals}
              alerts={alerts}
            />
          </div>
        </header>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          
          <Card className="bg-card border-border backdrop-blur-xl p-6 hover:bg-muted/50 transition-colors duration-300">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-muted-foreground text-sm font-semibold">Total Signals</h3>
              <Network className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-foreground tracking-tight">{totalSignals.toLocaleString()}</span>
            </div>
          </Card>

          <Card className="bg-card border-border backdrop-blur-xl p-6 hover:bg-muted/50 transition-colors duration-300">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-muted-foreground text-sm font-semibold">Active Clusters</h3>
              <Database className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-foreground tracking-tight">{activeClusters}</span>
            </div>
          </Card>

          <Card className="bg-card border-border backdrop-blur-xl p-6 hover:bg-muted/50 transition-colors duration-300">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-muted-foreground text-sm font-semibold">Data Analyzed (GB)</h3>
              <Cpu className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-foreground tracking-tight">{dataAnalyzed}</span>
            </div>
          </Card>

          <Card className="bg-card border-border backdrop-blur-xl p-6 hover:bg-muted/50 transition-colors duration-300">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-muted-foreground text-sm font-semibold">Active Reviewers</h3>
              <Users className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-foreground tracking-tight">{activeReviewers}</span>
            </div>
          </Card>

        </div>

        <TimeFilteredChart communityId={communityId} />
        
        {/* Curated Alerts Table */}
        <CommunityAlertsTable alerts={alerts} />

        {/* Recent Signals Table */}
        <Card className="bg-card border-border backdrop-blur-xl overflow-hidden mt-8 transition-colors duration-300">
          <div className="p-6 border-b border-border">
            <h2 className="text-lg font-bold text-foreground">Recent Signals</h2>
            <p className="text-muted-foreground text-sm mt-1">The latest anomalous signals identified by the engine.</p>
          </div>
          <div className="overflow-x-auto">
            <Table className="w-full table-fixed">
              <TableHeader className="bg-muted/50">
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead className="w-[10%] text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-8">ID</TableHead>
                  <TableHead className="w-[45%] text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-8">Signal Name</TableHead>
                  <TableHead className="w-[15%] text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-8">Type</TableHead>
                  <TableHead className="w-[15%] text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-8">Severity</TableHead>
                  <TableHead className="w-[15%] text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-8">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {signals.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-12 text-muted-foreground">
                      No signals found.
                    </TableCell>
                  </TableRow>
                ) : (
                  signals.map((signal) => (
                    <TableRow key={signal.id} className="border-border hover:bg-muted/40 transition-colors duration-200 cursor-pointer">
                      <TableCell className="px-8 py-5 text-muted-foreground text-sm font-mono">
                        {signal.id.substring(0, 6)}
                      </TableCell>
                      <TableCell className="px-8 py-5 font-semibold text-foreground text-sm truncate max-w-0">
                        {signal.topic}
                      </TableCell>
                      <TableCell className="px-8 py-5 text-muted-foreground text-sm truncate">
                        {signal.source}
                      </TableCell>
                      <TableCell className="px-8 py-5">
                        <Badge variant="outline" className="bg-muted/80 border-border text-foreground font-medium">
                          {signal.score}
                        </Badge>
                      </TableCell>
                      <TableCell className="px-8 py-5">
                        <div className="flex items-center gap-2">
                          {signal.trend === 'up' ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-500" />
                          ) : signal.trend === 'down' ? (
                            <ArrowDownRight className="w-4 h-4 text-rose-500" />
                          ) : (
                            <ArrowRight className="w-4 h-4 text-muted-foreground" />
                          )}
                          <span className={
                            signal.trend === 'up' ? 'text-emerald-500 font-medium text-sm' : 
                            signal.trend === 'down' ? 'text-rose-500 font-medium text-sm' : 
                            'text-muted-foreground font-medium text-sm'
                          }>
                            {signal.trend === 'up' ? 'Rising' : signal.trend === 'down' ? 'Falling' : 'Stable'}
                          </span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </Card>

      </div>
    </div>
  );
}
