"use client";

import React, { Fragment } from "react";
import { Area, AreaChart, CartesianGrid, ReferenceLine, ReferenceDot, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Parse ISO date string as LOCAL time, not UTC.
// new Date("2020-04-11") → UTC midnight → displays as Apr 10 in +5:30 timezone.
// Splitting and using Date(y, m-1, d) creates a local-timezone date → correct display.
function parseLocalDate(dateStr: string): Date {
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
  }
  return new Date(dateStr); // fallback for non-YYYY-MM-DD formats
}

function formatBucketLabel(dateStr: string, bucket: string): string {
  const d = parseLocalDate(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  // Use full 4-digit year for monthly to avoid "Apr 10" being read as "April 10th"
  if (bucket === 'month') {
    const month = d.toLocaleDateString('en-US', { month: 'short' });
    const year = d.getFullYear();
    return `${month} ${year}`;
  }
  if (bucket === 'week') return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatTooltipLabel(dateStr: string, bucket: string): string {
  const d = parseLocalDate(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  if (bucket === 'month') return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  if (bucket === 'week') return `Week of ${d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`;
  return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
}

export default function VolumeChart({ data, bucket = 'day', alerts = [] }: { data: any[], bucket?: string, alerts?: any[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[350px] w-full mt-6 flex items-center justify-center text-zinc-500 text-sm">
        No timeline data available.
      </div>
    );
  }

  // For monthly charts: select one tick per year in January (or the earliest available month that year)
  // This avoids index-based interval drift when zero-fill adds months without data
  let ticks: string[] | undefined = undefined;
  let tickInterval = 0;

  if (bucket === 'month') {
    // Build a map of year → first date seen for that year
    const yearFirstDate = new Map<number, string>();
    for (const d of data) {
      const year = parseInt(d.date.substring(0, 4));
      const month = parseInt(d.date.substring(5, 7));
      if (!yearFirstDate.has(year)) {
        yearFirstDate.set(year, d.date);
      }
      // Prefer January tick over whatever came first
      if (month === 1) {
        yearFirstDate.set(year, d.date);
      }
    }
    ticks = Array.from(yearFirstDate.values()).sort();
    // Fallback: if only one year, show every month
    if (ticks.length <= 1) ticks = undefined;
  } else {
    // For daily/weekly: index-based adaptive tick density
    tickInterval = data.length > 100 ? Math.floor(data.length / 12) :
                   data.length > 30  ? Math.floor(data.length / 8)  :
                   data.length > 10  ? Math.floor(data.length / 5)  : 0;
  }

  // Peak for reference line annotation
  const maxCount = Math.max(...data.map(d => d.post_count));
  const peakPoint = data.find(d => d.post_count === maxCount);

  // Cross-reference database alerts with chart data points
  let alertPoints: any[] = [];
  const chartData = data.map(d => ({ ...d, isAlert: false }));

  if (alerts && alerts.length > 0 && chartData.length > 0) {
    alerts.forEach(alert => {
      if (!alert.time_window) return;
      
      // 1. Extract clean YYYY-MM-DD and parse locally to avoid UTC drift
      const dateOnly = alert.time_window.split('T')[0].split(' ')[0];
      const alertTime = parseLocalDate(dateOnly).getTime();
      
      if (isNaN(alertTime)) return;
      
      // 2. Mathematically snap to the absolute closest date on the chart
      let matchIndex = -1;
      let minDiff = Infinity;
      
      chartData.forEach((d, idx) => {
        const dTime = parseLocalDate(d.date).getTime();
        if (!isNaN(dTime)) {
          const diff = Math.abs(dTime - alertTime);
          if (diff < minDiff) {
            minDiff = diff;
            matchIndex = idx;
          }
        }
      });
      
      // 3. Mark the matched point
      if (matchIndex !== -1) {
        chartData[matchIndex].isAlert = true;
      }
    });
    
    // 4. Extract uniquely marked points to avoid Recharts rendering overlapping dots
    alertPoints = chartData.filter(d => d.isAlert);
  }

  return (
    <div className="h-[350px] w-full mt-6">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 16, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#10b981" stopOpacity={0.35} />
              <stop offset="70%" stopColor="#10b981" stopOpacity={0.08} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#27272a"
            vertical={false}
          />

          <XAxis
            dataKey="date"
            allowDuplicatedCategory={false}
            stroke="#3f3f46"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickMargin={10}
            {...(ticks ? { ticks } : { interval: tickInterval })}
            tickFormatter={(tick) => formatBucketLabel(tick, bucket)}
          />

          <YAxis
            stroke="#3f3f46"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => value >= 1000 ? `${(value / 1000).toFixed(1)}k` : String(value)}
            width={40}
          />

          <Tooltip
            shared={false}
            isAnimationActive={false}
            contentStyle={{
              backgroundColor: '#09090b',
              borderColor: '#27272a',
              borderRadius: '10px',
              color: '#e4e4e7',
              fontSize: '13px',
              padding: '10px 14px',
              boxShadow: '0 4px 24px rgba(0,0,0,0.5)'
            }}
            itemStyle={{ color: '#10b981' }}
            labelStyle={{ color: '#a1a1aa', marginBottom: 4 }}
            labelFormatter={(label) => formatTooltipLabel(label as string, bucket)}
            formatter={(value: any) => [`${value.toLocaleString()} signals`, 'Volume']}
            cursor={{ stroke: '#10b981', strokeWidth: 1, strokeDasharray: '4 4' }}
          />

          {peakPoint && (
            <ReferenceLine
              x={peakPoint.date}
              stroke="#10b981"
              strokeOpacity={0.3}
              strokeDasharray="4 4"
              label={{
                value: `Peak: ${maxCount.toLocaleString()}`,
                position: 'top',
                fill: '#10b981',
                fontSize: 10,
                opacity: 0.7
              }}
            />
          )}

          {alertPoints.map((pt, idx) => (
            <Fragment key={`alert-${idx}`}>
              <ReferenceLine
                x={pt.date}
                stroke="#ef4444"
                strokeDasharray="3 3"
                opacity={0.5}
              />
              <ReferenceDot
                x={pt.date}
                y={pt.post_count}
                fill="#ef4444"
                stroke="#7f1d1d"
                strokeWidth={2}
                r={4}
              />
            </Fragment>
          ))}

          <Area
            type="basis"
            dataKey="post_count"
            stroke="#10b981"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorCount)"
            isAnimationActive={false}
            activeDot={(props: any) => {
              const { cx, cy, payload } = props;
              if (payload && payload.isAlert) {
                return <circle cx={cx} cy={cy} r={5} fill="#ef4444" stroke="#7f1d1d" strokeWidth={2} />;
              }
              return <circle cx={cx} cy={cy} r={5} fill="#10b981" stroke="#fff" strokeWidth={2} />;
            }}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
