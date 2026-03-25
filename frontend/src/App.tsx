import { useState } from 'react';
import { search } from './api';
import './App.css';
import type { EpisodeResult } from './models';

type Status = 'idle' | 'loading' | 'success' | 'error';

const App = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<EpisodeResult[] | null>(null);
  const [status, setStatus] = useState<Status>('idle');

  const handleSubmit = async (e: React.BaseSyntheticEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setStatus('loading');
    setResult(null);

    try {
      const response = await search(query);
      setResult(response);
      setStatus('success');
    } catch {
      setResult(null);
      setStatus('error');
    }
  };

  return (
    <main className="page">
      <div className="container">
        <h1>Simpson's Episode Lookup</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Homer gets a job at a bowling alley"
            disabled={status === 'loading'}
          />
          <button type="submit" disabled={status === 'loading' || !query.trim()}>
            {status === 'loading' ? 'Searching…' : 'Find Episode'}
          </button>
        </form>
        {status === 'error' && <p className="error">Something went wrong. Please try again.</p>}
        {result && (
          <div className="results">
            {result.map((episode, i) => (
              <div key={i} className="card">
                <div className="card-header">
                  <span className="card-title">{episode.title}</span>
                  <span className="card-meta">
                    S{episode.season} E{episode.episode_number} · {episode.airdate}
                  </span>
                </div>
                <p className="card-synopsis">{episode.synopsis}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
};

export default App;
