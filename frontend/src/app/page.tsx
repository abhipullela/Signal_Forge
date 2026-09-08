import CommunityOverviewCard from '../components/CommunityOverviewCard';
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
import { ArrowUpRight, ArrowDownRight, ArrowRight, Database, Gamepad2, Cpu } from "lucide-react";
import { fetchSignals, fetchStats, fetchCommunities, UISignal, SystemStats, CommunityOverview } from "@/lib/api";
import SearchBar from "@/components/SearchBar";

export default async function Home() {
  const [signals, stats, communities] = await Promise.all([
    fetchSignals(423),
    fetchStats(),
    fetchCommunities()
  ]);

  const getCommunity = (id: number) => communities.find(c => c.community_id === id) || {
    active_signals: 0,
    average_novelty: 0,
    total_posts: 0,
    alerts_count: 0
  };

  const formatVolume = (vol: number) => {
    if (vol > 1000000) return (vol / 1000000).toFixed(1) + "M";
    if (vol >= 1000) return (vol / 1000).toFixed(1) + "K";
    return vol.toString();
  };

  const datasets = getCommunity(423);
  const tech = getCommunity(424);
  const gaming = getCommunity(425);

  return (
    <div className="min-h-screen bg-background text-foreground p-6 md:p-12 font-sans relative overflow-hidden transition-colors duration-300">
      
      {/* Ambient Glow */}
      <div className="absolute top-[-150px] left-[-150px] w-[500px] h-[500px] bg-emerald-900/20 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto space-y-16 relative z-10">
        
        {/* Header / Global System Status */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center pt-4 pb-2">
          <div>
            <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
              SignalForge
            </h1>
            <div className="flex items-center gap-2 mt-3">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <p className="text-muted-foreground text-xs font-semibold uppercase tracking-widest">System Status: Operational</p>
            </div>
          </div>
          
          <div className="mt-8 md:mt-0 flex items-center gap-12">
            <SearchBar />
            <div className="hidden lg:flex gap-12">
              <div className="flex flex-col items-end">
                <span className="text-muted-foreground uppercase tracking-widest text-xs font-semibold mb-1">Total Monitored</span>
                <span className="text-2xl font-semibold text-foreground tabular-nums leading-none">{stats.total_monitored}</span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-muted-foreground uppercase tracking-widest text-xs font-semibold mb-1">Active Signals</span>
                <span className="text-2xl font-semibold text-foreground tabular-nums leading-none">{stats.active_signals}</span>
              </div>
            </div>
          </div>
        </header>

        {/* Community Key Cards Grid */}
        <section>
          <div className="mb-8">
            <h2 className="text-xl font-bold tracking-tight text-foreground">Communities</h2>
            <div className="h-[1px] w-full bg-border my-6" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <CommunityOverviewCard 
              id="datasets"
              name="Datasets"
              activeSignals={datasets.active_signals}
              aggregateNovelty={Number(datasets.average_novelty.toFixed(1))}
              messageVolume24h={formatVolume(datasets.total_posts)}
              alerts={datasets.alerts_count}
              icon={<Database className="w-5 h-5 text-zinc-400" />}
            />
            <CommunityOverviewCard 
              id="technology"
              name="Technology"
              activeSignals={tech.active_signals}
              aggregateNovelty={Number(tech.average_novelty.toFixed(1))}
              messageVolume24h={formatVolume(tech.total_posts)}
              alerts={tech.alerts_count}
              icon={<Cpu className="w-5 h-5 text-zinc-400" />}
            />
            <CommunityOverviewCard 
              id="gaming"
              name="Gaming"
              activeSignals={gaming.active_signals}
              aggregateNovelty={Number(gaming.average_novelty.toFixed(1))}
              messageVolume24h={formatVolume(gaming.total_posts)}
              alerts={gaming.alerts_count}
              icon={<Gamepad2 className="w-5 h-5 text-zinc-400" />}
            />
          </div>
        </section>

        {/* Emerging Signals Table */}
        <section>
          <div className="mb-8">
            <h2 className="text-xl font-bold tracking-tight text-foreground">Top Emerging Signals</h2>
            <div className="h-[1px] w-full bg-border my-6" />
          </div>
          
          <Card className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden transition-colors duration-300">
            <div className="overflow-x-auto">
              <Table className="table-fixed w-full">
                <TableHeader className="bg-muted/40">
                  <TableRow className="hover:bg-transparent border-border">
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5 w-1/2">TOPIC / CLUSTER</TableHead>
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5">SIGNAL SCORE</TableHead>
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5">PRIMARY SOURCE</TableHead>
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5">CURRENT TREND</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {signals.length === 0 ? (
                    <TableRow className="border-border hover:bg-muted/40 transition-colors duration-200">
                      <TableCell colSpan={4} className="px-8 py-12 text-center text-muted-foreground font-medium">
                        No signals found.
                      </TableCell>
                    </TableRow>
                  ) : (
                    signals.map((signal) => (
                      <TableRow key={signal.id} className="border-border hover:bg-muted/40 transition-colors duration-200 cursor-pointer">
                        <TableCell className="px-8 py-5 font-semibold text-foreground text-sm truncate max-w-0">
                          {signal.topic}
                        </TableCell>
                        <TableCell className="px-8 py-5">
                          <span className="font-semibold text-foreground text-sm tabular-nums">{signal.score}</span>
                        </TableCell>
                        <TableCell className="px-8 py-5 text-muted-foreground font-medium text-sm">
                          {signal.source}
                        </TableCell>
                        <TableCell className="px-8 py-5">
                          {signal.trend === 'up' && (
                            <Badge variant="outline" className="text-emerald-500 bg-emerald-500/10 border-emerald-500/20 font-bold tracking-wider uppercase text-[10px] rounded-full px-3 py-1">
                              <ArrowUpRight className="mr-1.5 h-3 w-3" />
                              Rising
                            </Badge>
                          )}
                          {signal.trend === 'down' && (
                            <Badge variant="outline" className="text-red-500 bg-red-500/10 border-red-500/20 font-bold tracking-wider uppercase text-[10px] rounded-full px-3 py-1">
                              <ArrowDownRight className="mr-1.5 h-3 w-3" />
                              Falling
                            </Badge>
                          )}
                          {signal.trend === 'flat' && (
                            <Badge variant="outline" className="text-muted-foreground bg-muted border-border font-bold tracking-wider uppercase text-[10px] rounded-full px-3 py-1">
                              <ArrowRight className="mr-1.5 h-3 w-3" />
                              Stable
                            </Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </Card>
        </section>
        
      </div>
    </div>
  );
}
