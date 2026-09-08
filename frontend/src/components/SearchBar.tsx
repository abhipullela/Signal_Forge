"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { searchSignals, UISignal } from "@/lib/api";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<UISignal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.trim().length > 1) {
        setIsLoading(true);
        const data = await searchSignals(query);
        setResults(data);
        setIsLoading(false);
        setIsOpen(true);
      } else {
        setResults([]);
        setIsOpen(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Handle clicking outside to close
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleResultClick = (id: string) => {
    setIsOpen(false);
    setQuery("");
    router.push(`/signal/${id}`);
  };

  return (
    <div className="relative w-full max-w-sm" ref={dropdownRef}>
      <div className="relative flex items-center w-full h-10 rounded-md border border-border bg-card/50 backdrop-blur-xl px-3 py-2 text-sm overflow-hidden focus-within:ring-1 focus-within:ring-emerald-500/50 focus-within:border-emerald-500/50 transition-all">
        <Search className="mr-2 h-4 w-4 shrink-0 text-muted-foreground" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search topics, posts, or keywords..."
          className="flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground truncate"
        />
        {isLoading && <Loader2 className="ml-2 h-4 w-4 shrink-0 text-muted-foreground animate-spin" />}
      </div>

      {isOpen && query.trim().length > 1 && (
        <div className="absolute top-full mt-2 w-full rounded-md border border-border bg-card shadow-lg overflow-hidden z-50">
          <ul className="max-h-[300px] overflow-y-auto p-1">
            {results.length === 0 && !isLoading ? (
              <li className="px-3 py-4 text-center text-sm text-muted-foreground">
                No results found.
              </li>
            ) : (
              results.map((signal) => (
                <li
                  key={signal.id}
                  onClick={() => handleResultClick(signal.id)}
                  className="flex flex-col gap-1 px-3 py-2 hover:bg-muted/80 cursor-pointer rounded-sm transition-colors group"
                >
                  <span className="text-sm font-medium text-foreground group-hover:text-emerald-500 transition-colors truncate">
                    {signal.topic}
                  </span>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span className="truncate">{signal.source}</span>
                    <span className="shrink-0">{signal.score}</span>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
