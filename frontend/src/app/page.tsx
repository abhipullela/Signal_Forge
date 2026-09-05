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

interface Signal {
  id: string;
  topic: string;
  score: number;
  community: string;
  trend: 'up' | 'down' | 'flat';
}

// Mock Data
const MOCK_SIGNALS: Signal[] = [
  { id: '1', topic: 'AI Agent Workflows', score: 94.2, community: 'Technology', trend: 'up' },
  { id: '2', topic: 'Next.js 15 Migration', score: 88.5, community: 'Technology', trend: 'up' },
  { id: '3', topic: 'Rust Web Frameworks', score: 82.1, community: 'Datasets', trend: 'flat' },
  { id: '4', topic: 'Local LLM Inference', score: 91.0, community: 'Technology', trend: 'up' },
  { id: '5', topic: 'Serverless Databases', score: 76.4, community: 'Datasets', trend: 'down' },
  { id: '6', topic: 'Cloud Gaming APIs', score: 86.8, community: 'Gaming', trend: 'up' },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-foreground p-6 md:p-12 font-sans relative overflow-hidden">
      
      {/* Ambient Glow */}
      <div className="absolute top-[-150px] left-[-150px] w-[500px] h-[500px] bg-emerald-900/20 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto space-y-16 relative z-10">
        
        {/* Header / Global System Status */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center pt-4 pb-2">
          <div>
            <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-zinc-100 to-zinc-500 bg-clip-text text-transparent">
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
          
          <div className="mt-8 md:mt-0 flex gap-12">
            <div className="flex flex-col items-end">
              <span className="text-zinc-500 uppercase tracking-widest text-xs font-semibold mb-1">Total Monitored</span>
              <span className="text-2xl font-semibold text-zinc-100 tabular-nums leading-none">14.2M</span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-zinc-500 uppercase tracking-widest text-xs font-semibold mb-1">Active Signals</span>
              <span className="text-2xl font-semibold text-zinc-100 tabular-nums leading-none">342</span>
            </div>
          </div>
        </header>

        {/* Community Key Cards Grid */}
        <section>
          <div className="mb-8">
            <h2 className="text-xl font-bold tracking-tight text-white">Communities</h2>
            <div className="h-[1px] w-full bg-zinc-800/60 my-6" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <CommunityOverviewCard 
              id="datasets"
              name="Datasets"
              activeSignals={156}
              aggregateNovelty={78.4}
              messageVolume24h="4.2M"
              icon={<Database className="w-5 h-5 text-zinc-400" />}
            />
            <CommunityOverviewCard 
              id="technology"
              name="Technology"
              activeSignals={89}
              aggregateNovelty={82.1}
              messageVolume24h="8.1M"
              icon={<Cpu className="w-5 h-5 text-zinc-400" />}
            />
            <CommunityOverviewCard 
              id="gaming"
              name="Gaming"
              activeSignals={97}
              aggregateNovelty={85.6}
              messageVolume24h="12.5M"
              icon={<Gamepad2 className="w-5 h-5 text-zinc-400" />}
            />
          </div>
        </section>

        {/* Emerging Signals Table */}
        <section>
          <div className="mb-8">
            <h2 className="text-xl font-bold tracking-tight text-white">Top Emerging Signals</h2>
            <div className="h-[1px] w-full bg-zinc-800/60 my-6" />
          </div>
          
          <Card className="bg-zinc-950 border border-zinc-800 rounded-2xl shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-black/40">
                  <TableRow className="hover:bg-transparent border-zinc-800">
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5">Topic / Cluster</TableHead>
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5">Signal Score</TableHead>
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5">Primary Source</TableHead>
                    <TableHead className="font-semibold text-muted-foreground uppercase tracking-widest text-xs px-8 py-5">Current Trend</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {MOCK_SIGNALS.map((signal) => (
                    <TableRow key={signal.id} className="border-zinc-800 hover:bg-zinc-900/40 transition-colors duration-200 cursor-pointer">
                      <TableCell className="px-8 py-5 font-semibold text-white text-sm">
                        {signal.topic}
                      </TableCell>
                      <TableCell className="px-8 py-5">
                        <span className="font-semibold text-white text-sm tabular-nums">{signal.score.toFixed(1)}</span>
                      </TableCell>
                      <TableCell className="px-8 py-5 text-muted-foreground font-medium text-sm">
                        {signal.community}
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
                          <Badge variant="outline" className="text-muted-foreground bg-muted/20 border-zinc-700 font-bold tracking-wider uppercase text-[10px] rounded-full px-3 py-1">
                            <ArrowRight className="mr-1.5 h-3 w-3" />
                            Stable
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Card>
        </section>
        
      </div>
    </div>
  );
}
