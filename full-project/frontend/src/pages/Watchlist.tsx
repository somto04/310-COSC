import { useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL;

export default function WatchlistPage() {
  type Movie = {
    id: number;
    tmdbId?: number;
    title: string;
    poster?: string | null;
    overview?: string;
    rating?: number;
  };
    
    
  return (
    <div style={{ padding: "2rem" }}>
      <h1>Watchlist</h1>
    </div>
  );
}
