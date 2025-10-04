import React, { useState, useEffect } from 'react';
import { Search, Filter, FileText, Calendar, User, MapPin, Loader } from 'lucide-react';

const DocumentSearch = ({ onResultSelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [useLLM, setUseLLM] = useState(true);
  const [searchType, setSearchType] = useState('all');
  const [searchParams, setSearchParams] = useState(null);

  const performSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/unstructured/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          use_llm: useLLM,
          search_type: searchType
        })
      });

      const data = await response.json();

      if (data.success) {
        // Handle new integrated search response format
        const integratedResults = data.results;
        setResults(integratedResults);

        // Set search parameters for display
        setSearchParams({
          query: integratedResults.query,
          search_type: integratedResults.search_type,
          neo4j_count: integratedResults.neo4j_results?.length || 0,
          solr_count: integratedResults.solr_results?.length || 0,
          insights: integratedResults.combined_insights || []
        });
      } else {
        console.error('Search failed:', data.error);
        setResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      performSearch();
    }
  };

  const highlightKeywords = (text, keywords) => {
    if (!keywords || keywords.length === 0) return text;

    let highlightedText = text;
    keywords.forEach(keyword => {
      const regex = new RegExp(`(${keyword})`, 'gi');
      highlightedText = highlightedText.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
    });

    return highlightedText;
  };

  const formatScore = (score) => {
    return (score * 100).toFixed(1) + '%';
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Document Search</h2>
        <p className="text-gray-600">
          Search through processed documents using natural language queries
        </p>
      </div>

      {/* Search Input */}
      <div className="mb-6">
        <div className="flex gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter your search query..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={performSearch}
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {loading ? (
              <Loader className="animate-spin h-4 w-4" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            Search
          </button>
        </div>

        {/* Search Options */}
        <div className="flex items-center gap-4 flex-wrap">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={useLLM}
              onChange={(e) => setUseLLM(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Use AI understanding</span>
          </label>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Search in:</span>
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Sources</option>
              <option value="structured">Knowledge Graph Only</option>
              <option value="unstructured">Documents Only</option>
            </select>
          </div>

          <span className="text-xs text-gray-500">
            Integrated search combines Neo4j graph data with document search
          </span>
        </div>
      </div>

      {/* Search Parameters Display */}
      {searchParams && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-medium text-blue-800 mb-2">Search Results Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-blue-700">Query:</span>
              <span className="ml-2 text-blue-600">"{searchParams.query}"</span>
            </div>
            <div>
              <span className="font-medium text-blue-700">Search Type:</span>
              <span className="ml-2 text-blue-600">{searchParams.search_type}</span>
            </div>
            <div>
              <span className="font-medium text-blue-700">Sources:</span>
              <span className="ml-2 text-blue-600">
                {searchParams.neo4j_count} graph + {searchParams.solr_count} documents
              </span>
            </div>
          </div>

          {searchParams.insights && searchParams.insights.length > 0 && (
            <div className="mt-3">
              <span className="font-medium text-blue-700">AI Insights:</span>
              <ul className="mt-1 text-sm text-blue-600">
                {searchParams.insights.map((insight, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Search Results */}
      <div className="space-y-6">
        {loading && (
          <div className="text-center py-8">
            <Loader className="animate-spin h-8 w-8 mx-auto text-blue-600 mb-4" />
            <p className="text-gray-600">Searching across knowledge graph and documents...</p>
          </div>
        )}

        {!loading && !results.neo4j_results?.length && !results.solr_results?.length && query && (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No results found for "{query}"</p>
            <p className="text-sm text-gray-500 mt-2">
              Try different keywords or check if data has been indexed
            </p>
          </div>
        )}

        {/* Neo4j Graph Results */}
        {results.neo4j_results && results.neo4j_results.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              Knowledge Graph Results ({results.neo4j_results.length})
            </h3>
            <div className="space-y-3">
              {results.neo4j_results.map((result, index) => (
                <div
                  key={`neo4j-${index}`}
                  className="border border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer bg-green-50"
                  onClick={() => onResultSelect?.(result)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <h4 className="font-medium text-gray-800">{result.label}</h4>
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        {result.group}
                      </span>
                    </div>
                  </div>

                  {result.properties && (
                    <div className="text-sm text-gray-600">
                      {Object.entries(result.properties).slice(0, 3).map(([key, value]) => (
                        <div key={key} className="mb-1">
                          <span className="font-medium">{key}:</span> {String(value)}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Solr Document Results */}
        {results.solr_results && results.solr_results.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              Document Results ({results.solr_results.length})
            </h3>
            <div className="space-y-3">
              {results.solr_results.map((result, index) => (
                <div
                  key={`solr-${index}`}
                  className="border border-blue-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer bg-blue-50"
                  onClick={() => onResultSelect?.(result)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-blue-500" />
                      <h4 className="font-medium text-gray-800">{result.id || `Document ${index + 1}`}</h4>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {result.type || 'document'}
                      </span>
                    </div>
                  </div>

                  {result.content && (
                    <div className="text-sm text-gray-600 mb-2">
                      {result.content.length > 200 ? `${result.content.substring(0, 200)}...` : result.content}
                    </div>
                  )}

                  {result.prop_filename && (
                    <div className="text-xs text-gray-500">
                      File: {result.prop_filename}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Ollama Context */}
        {results.ollama_context && (
          <div className="mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h3 className="font-medium text-purple-800 mb-2 flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              AI Analysis
            </h3>
            <div className="text-sm text-purple-700">
              {results.ollama_context.summary || 'Analysis in progress...'}
            </div>
          </div>
        )}
      </div>

      {/* Results Summary */}
      {!loading && (results.neo4j_results?.length > 0 || results.solr_results?.length > 0) && (
        <div className="mt-6 text-center text-sm text-gray-600">
          Found {results.neo4j_results?.length || 0} graph results + {results.solr_results?.length || 0} document results for "{query}"
        </div>
      )}
    </div>
  );
};

export default DocumentSearch;