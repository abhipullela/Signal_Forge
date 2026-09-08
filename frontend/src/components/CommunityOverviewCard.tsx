import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface CommunityOverviewCardProps {
  id: string;
  name: string;
  activeSignals: number;
  aggregateNovelty: number;
  messageVolume24h: string;
  icon: React.ReactNode;
}

export default function CommunityOverviewCard({
  id,
  name,
  activeSignals,
  aggregateNovelty,
  messageVolume24h,
  icon,
}: CommunityOverviewCardProps) {
  return (
    <Link href={`/community/${id}`} className="block h-full cursor-pointer">
      <Card className="group h-full bg-zinc-950 border border-zinc-800 border-t-zinc-700/50 shadow-lg shadow-black/50 rounded-2xl overflow-hidden transition-all duration-300 ease-out hover:-translate-y-1.5 hover:scale-[1.01] hover:shadow-xl hover:shadow-white/[0.02] hover:border-zinc-600 hover:bg-zinc-900/80">
        <CardHeader className="p-6 pb-4">
          <CardTitle className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            {icon}
            {name}
          </CardTitle>
        </CardHeader>
        
        <Separator className="bg-zinc-800 transition-colors duration-300 group-hover:bg-zinc-700" />

        <CardContent className="p-6 pt-4">
          <div className="flex flex-col space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground group-hover:text-zinc-400 transition-colors text-xs font-semibold tracking-widest uppercase">Active Signals</span>
              <span className="text-xl font-semibold text-white tabular-nums">{activeSignals}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground group-hover:text-zinc-400 transition-colors text-xs font-semibold tracking-widest uppercase">Avg Novelty</span>
              <span className="text-xl font-semibold text-white tabular-nums">{aggregateNovelty.toFixed(1)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground group-hover:text-zinc-400 transition-colors text-xs font-semibold tracking-widest uppercase">24h Volume</span>
              <span className="text-xl font-semibold text-white tabular-nums">{messageVolume24h}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
