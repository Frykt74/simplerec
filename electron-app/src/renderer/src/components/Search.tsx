import React, { useState } from 'react';
import { SearchResult } from '../types/api';

const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.length < 2) return;
    
    setSearching(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/search?q=${encodeURIComponent(query)}&limit=20`
      );
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Поиск по содержимому документов..."
          className="search-input"
        />
        <button type="submit" disabled={searching || query.length < 2}>
          {searching ? '⏳' : '🔍'} Искать
        </button>
      </form>

      {results.length > 0 && (
        <div className="search-results">
          <h3>Найдено результатов: {results.length}</h3>
          {results.map((result, index) => (
            <div key={index} className="search-result-item">
              <h4>📄 {result.filename}</h4>
              <p className="snippet">{result.snippet}</p>
              <div className="result-meta">
                <span>Релевантность: {(result.rank * 100).toFixed(0)}%</span>
                <button
                  onClick={() => window.open(
                    `http://localhost:8000/api/v1/documents/${result.document_id}`,
                    '_blank'
                  )}
                  className="btn-view-doc"
                >
                  Открыть документ
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && query && !searching && (
        <div className="no-results">
          <p>Ничего не найдено по запросу "{query}"</p>
        </div>
      )}
    </div>
  );
};

export default Search;
