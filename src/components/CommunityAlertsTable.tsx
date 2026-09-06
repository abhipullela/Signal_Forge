"use client";

import { useState } from "react";
import { AlertData } from "@/lib/api";
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
import { ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";

export function CommunityAlertsTable({ alerts }: { alerts: AlertData[] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!alerts || alerts.length === 0) {
    return null;
  }

  return (
    <Card className="bg-card border-border backdrop-blur-xl overflow-hidden mt-8 transition-colors duration-300">
      <div 
        className="p-6 border-b border-border flex justify-between items-center cursor-pointer hover:bg-muted/30 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div>
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-destructive" />
            Curated Alerts Overview
            <Badge variant="outline" className="ml-2 bg-destructive/10 text-destructive border-destructive/20">
              {alerts.length}
            </Badge>
          </h2>
          <p className="text-muted-foreground text-sm mt-1">Detailed CSV metrics for alerts in this community.</p>
        </div>
        <div>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-muted-foreground" />
          ) : (
            <ChevronDown className="w-5 h-5 text-muted-foreground" />
          )}
        </div>
      </div>
      
      <div className={`grid transition-all duration-300 ease-in-out ${isExpanded ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}>
        <div className="overflow-hidden">
          <div className="overflow-x-auto">
            <Table className="w-full">
              <TableHeader className="bg-muted/50">
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Cluster ID</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Volume</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Growth Rate</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Velocity</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Acceleration</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Comm. Spread</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Risk Type</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Priority</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Level</TableHead>
                  <TableHead className="text-muted-foreground uppercase text-xs tracking-wider font-semibold py-4 px-6 whitespace-nowrap">Source Posts</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.map((alert, i) => (
                  <TableRow key={i} className="border-border hover:bg-muted/40 transition-colors duration-200">
                    <TableCell className="px-6 py-4 font-mono text-foreground text-sm">{alert.cluster_id}</TableCell>
                    <TableCell className="px-6 py-4 text-foreground text-sm tabular-nums">{alert.volume.toFixed(1)}</TableCell>
                    <TableCell className="px-6 py-4 text-foreground text-sm tabular-nums">{alert.growth_rate.toFixed(2)}</TableCell>
                    <TableCell className="px-6 py-4 text-foreground text-sm tabular-nums">{alert.velocity.toFixed(2)}</TableCell>
                    <TableCell className="px-6 py-4 text-foreground text-sm tabular-nums">{alert.acceleration.toFixed(2)}</TableCell>
                    <TableCell className="px-6 py-4 text-foreground text-sm tabular-nums">{alert.community_spread_score.toFixed(2)}</TableCell>
                    <TableCell className="px-6 py-4">
                      <Badge variant="outline" className="bg-muted/80 border-border text-foreground capitalize">{alert.risk_type || "N/A"}</Badge>
                    </TableCell>
                    <TableCell className="px-6 py-4">
                      <span className={
                        alert.alert_priority?.toLowerCase() === 'high' ? 'text-destructive font-medium' :
                        alert.alert_priority?.toLowerCase() === 'medium' ? 'text-orange-500 font-medium' :
                        'text-emerald-500 font-medium'
                      }>
                        {alert.alert_priority || "N/A"}
                      </span>
                    </TableCell>
                    <TableCell className="px-6 py-4 text-muted-foreground text-sm">{alert.alert_level || "N/A"}</TableCell>
                    <TableCell className="px-6 py-4 text-foreground text-sm tabular-nums">{alert.source_post_count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </Card>
  );
}
