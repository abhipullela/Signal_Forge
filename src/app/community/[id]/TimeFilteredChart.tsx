"use client";

import { useState, useEffect, useCallback } from "react";
import VolumeChart from "./VolumeChart";
import { Card } from "@/components/ui/card";

type FilterKey = 'all' | '90' | '30' | '7';

interface VolumeDataPoint {
  date: string;
  post_count: number;
  average_signal_score: number;
}

const FILTERS: { key: FilterKey; label: string; days?: number }[] = [
  { key: 'all',  label: 'All time' },
  { key: '90',   label: 'Last 3 months', days: 90 },
  { key: '30',   label: 'Last 30 days',  days: 30 },
  { key: '7',    label: 'Last 7 days',   days: 7 },
];

export default function TimeFilteredChart({ communityId }: { communityId: string }) {
  const [activeFilter, setActiveFilter] = useState<FilterKey>('all');
  const [data, setData] = useState<VolumeDataPoint[]>([]);
  const [bucket, setBucket] = useState<string>('day');
  const [loading, setLoading] = useState(true);

  const fetchTrend = useCallback(async (filter: FilterKey) => {
    setLoading(true);
    try {
      const filterDef = FILTERS.find(f => f.key === filter);
      const url = filterDef?.days
        ? `http://localhost:8000/api/community/${communityId}/trend?days=${filterDef.days}`
        : `http://localhost:8000/api/community/${communityId}/trend`;

      const res = await fetch(url, { cache: 'no-store' });
      if (!res.ok) throw new Error('Failed to fetch trend');
      const json = await res.json();
      setData(json.trend || []);
      setBucket(json.bucket || 'day');
    } catch (e) {
      console.error('TimeFilteredChart fetch error:', e);
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [communityId]);

  // Fetch full history on mount
  useEffect(() => {
    fetchTrend('all');
  }, [fetchTrend]);

  const handleFilter = (key: FilterKey) => {
    setActiveFilter(key);
    fetchTrend(key);
  };

  return (
    <Card className="bg-card border-border backdrop-blur-xl p-6 transition-colors duration-300">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h2 className="text-lg font-bold text-foreground">Signal Volume</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Volume of detected signals over the selected time period.
          </p>
        </div>
        <div className="flex gap-1 mt-4 md:mt-0 bg-muted/50 rounded-md p-1 border border-border">
          {FILTERS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => handleFilter(key)}
              className={`px-3 py-1.5 text-xs font-semibold rounded transition-all duration-150 ${
                activeFilter === key
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-[350px] w-full mt-6 flex items-center justify-center">
          <div className="flex items-center gap-3 text-muted-foreground text-sm">
            <span className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            Loading chart data...
          </div>
        </div>
      ) : (
        <VolumeChart data={data} bucket={bucket} />
      )}
    </Card>
  );
}
