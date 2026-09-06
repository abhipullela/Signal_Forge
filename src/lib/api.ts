export interface RawSignal {
  post_id: number;
  title: string | null;
  cluster_id: number | null;
  domain: string | null;
  cluster_size: number | null;
  cluster_rank: number | null;
  signal_score: number | null;
  signal_status: string | null;
  published_at: string | null;
}

export interface BackendResponse {
  community_id: number;
  signals: RawSignal[];
}

export interface UISignal {
  id: string;
  topic: string;
  score: string;
  source: string;
  trend: 'up' | 'down' | 'flat';
}

export async function fetchSignals(communityId: string | number): Promise<UISignal[]> {
  try {
    const res = await fetch(`http://localhost:8000/api/community/${communityId}/signals`, {
      cache: 'no-store'
    });
    
    if (!res.ok) {
      throw new Error(`Failed to fetch signals: ${res.status} ${res.statusText}`);
    }

    const rawData = await res.json();
    console.log("Raw Backend Data:", JSON.stringify(rawData, null, 2));

    let rawSignals: RawSignal[] = [];
    if (Array.isArray(rawData)) {
      rawSignals = rawData;
    } else if (rawData && Array.isArray(rawData.signals)) {
      rawSignals = rawData.signals;
    } else {
      console.warn("Unexpected API response shape:", rawData);
      return [];
    }

    return rawSignals.map((signal) => {
      const rawScore = signal.signal_score ?? 0;
      const scoreStr = (rawScore / 100).toFixed(1) + "x strength";

      let trend: 'up' | 'down' | 'flat' = 'flat';
      const status = (signal.signal_status || "").toUpperCase();
      
      if (status === 'RISING' || status === 'HIGH') trend = 'up';
      else if (status === 'FALLING' || status === 'LOW') trend = 'down';

      let sourceStr = 'Direct / Organic';
      if (signal.domain && signal.domain !== 'NaN' && signal.domain !== 'null') {
        sourceStr = signal.domain;
      } else if (signal.cluster_id) {
        sourceStr = `Cluster ${signal.cluster_id}`;
      } else {
        sourceStr = `Community ${communityId}`;
      }

      return {
        id: String(signal.post_id || Math.random()),
        topic: signal.title || "Unnamed Signal",
        score: scoreStr,
        source: sourceStr,
        trend: trend
      };
    });
  } catch (error) {
    console.error("fetchSignals Error:", error);
    return [];
  }
}

export interface SystemStats {
  total_monitored: string;
  active_signals: number;
}

export async function fetchStats(): Promise<SystemStats> {
  try {
    const res = await fetch(`http://localhost:8000/api/stats`, {
      cache: 'no-store'
    });
    
    if (!res.ok) {
      throw new Error(`Failed to fetch stats: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error("fetchStats Error:", error);
    return {
      total_monitored: "0",
      active_signals: 0
    };
  }
}

export interface CommunityOverview {
  community_id: number;
  total_posts: number;
  active_signals: number;
  average_novelty: number;
  alerts?: number;
}

export async function fetchCommunities(): Promise<CommunityOverview[]> {
  try {
    const res = await fetch(`http://localhost:8000/api/communities`, {
      cache: 'no-store'
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch communities`);
    }
    const data = await res.json();
    return data.communities || [];
  } catch (error) {
    console.error("fetchCommunities Error:", error);
    return [];
  }
}

export interface AlertData {
  cluster_id: number;
  volume: number;
  growth_rate: number;
  velocity: number;
  acceleration: number;
  community_spread_score: number;
  risk_type: string;
  alert_priority: string;
  alert_level: string;
  source_post_count: number;
}

export async function fetchCommunityAlerts(id: string | number): Promise<AlertData[]> {
  try {
    const res = await fetch(`http://localhost:8000/api/community/${id}/alerts`, {
      cache: 'no-store'
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch community alerts`);
    }
    const data = await res.json();
    return data.alerts || [];
  } catch (error) {
    console.error("fetchCommunityAlerts Error:", error);
    return [];
  }
}

export interface DetailedCommunityOverview {
  community_id: number;
  total_posts_analyzed: number;
  active_signals: number;
  active_clusters: number;
  average_signal_score: number;
}

export async function fetchCommunityOverviewById(id: string | number): Promise<DetailedCommunityOverview | null> {
  try {
    const res = await fetch(`http://localhost:8000/api/community/${id}/overview`, {
      cache: 'no-store'
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error("fetchCommunityOverviewById error:", e);
    return null;
  }
}

export interface VolumeDataPoint {
  date: string;
  post_count: number;
  average_signal_score: number;
}

export interface CommunityVolumeResponse {
  trend: VolumeDataPoint[];
  bucket: string;
}

export async function fetchCommunityVolume(id: string | number): Promise<CommunityVolumeResponse> {
  try {
    const res = await fetch(`http://localhost:8000/api/community/${id}/trend`, {
      cache: 'no-store'
    });
    if (!res.ok) return { trend: [], bucket: 'day' };
    const data = await res.json();
    return { trend: data.trend || [], bucket: data.bucket || 'day' };
  } catch (e) {
    console.error("fetchCommunityVolume error:", e);
    return { trend: [], bucket: 'day' };
  }
}

export interface SignalDetail {
  post_id: number;
  community_id: number;
  title: string | null;
  content: string | null;
  cluster_id: number | null;
  cluster_size: number | null;
  cluster_rank: number | null;
  signal_score: number | null;
  signal_status: string | null;
  published_at: string | null;
  url: string | null;
}

export async function fetchSignalDetails(postId: string | number): Promise<SignalDetail | null> {
  try {
    const res = await fetch(`http://localhost:8000/api/signal/${postId}`, {
      cache: 'no-store'
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error("fetchSignalDetails error:", e);
    return null;
  }
}

export async function searchSignals(query: string, communityId?: string): Promise<UISignal[]> {
  if (!query) return [];
  try {
    const url = new URL(`http://localhost:8000/api/search`);
    url.searchParams.append("query", query);
    if (communityId) {
      url.searchParams.append("community_id", communityId);
    }
    const res = await fetch(url.toString(), { cache: 'no-store' });
    if (!res.ok) return [];
    
    const data = await res.json();
    const rawSignals: RawSignal[] = data.signals || [];
    
    return rawSignals.map((signal) => {
      const rawScore = signal.signal_score ?? 0;
      const scoreStr = (rawScore / 100).toFixed(1) + "x strength";

      let trend: 'up' | 'down' | 'flat' = 'flat';
      const status = (signal.signal_status || "").toUpperCase();
      
      if (status === 'RISING' || status === 'HIGH') trend = 'up';
      else if (status === 'FALLING' || status === 'LOW') trend = 'down';

      let sourceStr = 'Direct / Organic';
      if (signal.domain && signal.domain !== 'NaN' && signal.domain !== 'null') {
        sourceStr = signal.domain;
      } else if (signal.cluster_id) {
        sourceStr = `Cluster ${signal.cluster_id}`;
      } else {
        sourceStr = "Global";
      }

      return {
        id: String(signal.post_id || Math.random()),
        topic: signal.title || "Unnamed Signal",
        score: scoreStr,
        source: sourceStr,
        trend: trend
      };
    });
  } catch (e) {
    console.error("searchSignals error:", e);
    return [];
  }
}
