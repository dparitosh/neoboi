import React, { useState } from 'react';
import { Search, Loader, FileText } from 'lucide-react';

const DocumentSearch = ({ onResultSelect }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('all'); // 'all', 'documents', 'graph'
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch(`/api/unstructured/search?query=${encodeURIComponent(query)}&type=${searchType}`, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // The backend nests results, so we need to extract them
      const combinedResults = [
        ...(data.results?.neo4j_results || []),
        ...(data.results?.solr_results || [])
      ];
      setResults(combinedResults);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const renderResultItem = (result) => {
    // Check if it's a graph node
    if (result.label && result.group) {
      return (
        <div className="flex items-center gap-4">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <div>
            <p className="font-semibold text-gray-800">{result.label}</p>
            <p className="text-sm text-gray-600">Graph Entity</p>
          </div>
        </div>
      );
    }

    // Assume it's a document
    return (
      <div className="flex items-center gap-4">
        <FileText className="h-5 w-5 text-blue-500" />
        <div>
          <p className="font-semibold text-gray-800">{result.id || result.filename || 'Document'}</p>
          <p className="text-sm text-gray-600">
            {result.content ? `${result.content.substring(0, 80)}...` : 'No preview available'}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full max-w-3xl mx-auto p-6 bg-gray-200">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Search Across Your Data</h2>
        <p className="text-gray-600">
          Query both processed documents and the knowledge graph.
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your search query..."
            className="flex-grow px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={searchType}
            onChange={(e) => setSearchType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All</option>
            <option value="documents">Documents</option>
            <option value="graph">Graph</option>
          </select>
          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center justify-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {isLoading ? (
              <Loader className="animate-spin h-5 w-5" />
            ) : (
              <Search className="h-5 w-5" />
            )}
            <span className="ml-2">Search</span>
          </button>
        </div>
      </form>

      {/* Results */}
      <div className="space-y-3">
        {error && (
          <div className="p-4 bg-red-100 text-red-700 border border-red-200 rounded-md">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results.length > 0 && (
          <h3 className="text-lg font-medium text-gray-800">
            Found {results.length} result{results.length !== 1 ? 's' : ''}
          </h3>
        )}

        {results.map((result, index) => (
          <div
            key={index}
            onClick={() => onResultSelect(result)}
            className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md cursor-pointer transition-shadow"
          >
            {renderResultItem(result)}
          </div>
        ))}

        {!isLoading && !error && results.length === 0 && query && (
          <div className="text-center py-8">
            <p className="text-gray-600">No results found for "{query}".</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentSearch;