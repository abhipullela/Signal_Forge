import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface CommunityOverviewCardProps {
  id: string;
  name: string;
  activeSignals: number;
  aggregateNovelty: number;
  messageVolume24h: string;
  alerts?: number;
  icon: React.ReactNode;
}

export default function CommunityOverviewCard({
  id,
  name,
  activeSignals,
  aggregateNovelty,
  messageVolume24h,
  alerts,
  icon,
}: CommunityOverviewCardProps) {
  return (
    <Link href={`/community/${id}`} className="block h-full cursor-pointer">
      <Card className="group h-full bg-card border border-border shadow-lg rounded-2xl overflow-hidden transition-all duration-300 ease-out hover:-translate-y-1.5 hover:scale-[1.01] hover:shadow-xl hover:border-muted-foreground/30 hover:bg-muted/30">
        <CardHeader className="p-6 pb-4">
          <CardTitle className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
            {icon}
            {name}
          </CardTitle>
        </CardHeader>
        
        <Separator className="bg-border transition-colors duration-300 group-hover:bg-muted-foreground/20" />

        <CardContent className="p-6 pt-4">
          <div className="flex flex-col space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground group-hover:text-foreground transition-colors text-xs font-semibold tracking-widest uppercase">Active Signals</span>
              <span className="text-xl font-semibold text-foreground tabular-nums">{activeSignals}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground group-hover:text-foreground transition-colors text-xs font-semibold tracking-widest uppercase">Avg Novelty</span>
              <span className="text-xl font-semibold text-foreground tabular-nums">{aggregateNovelty.toFixed(1)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground group-hover:text-foreground transition-colors text-xs font-semibold tracking-widest uppercase">24h Volume</span>
              <span className="text-xl font-semibold text-foreground tabular-nums">{messageVolume24h}</span>
            </div>
            
            {alerts !== undefined && (
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground group-hover:text-foreground transition-colors text-xs font-semibold tracking-widest uppercase">Alerts</span>
                <span className="text-xl font-semibold text-destructive tabular-nums">{alerts}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
