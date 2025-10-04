import React, { useState, useEffect } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentSearch from '../components/DocumentSearch';
import { FileText, Search, Upload, BarChart3, Settings } from 'lucide-react';

const UnstructuredDataPage = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [serviceStatus, setServiceStatus] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);

  useEffect(() => {
    checkServiceStatus();
  }, []);

  const checkServiceStatus = async () => {
    try {
      const response = await fetch('/api/unstructured/status');
      const data = await response.json();
      setServiceStatus(data.services);
    } catch (error) {
      console.error('Failed to check service status:', error);
    }
  };

  const tabs = [
    { id: 'upload', label: 'Upload Documents', icon: Upload },
    { id: 'search', label: 'Search Documents', icon: Search },
    { id: 'results', label: 'Search Results', icon: FileText },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'upload':
        return (
          <DocumentUpload
            onUploadComplete={(result) => {
              console.log('Upload completed:', result);
              // Could automatically switch to search tab or show success message
            }}
          />
        );

      case 'search':
        return (
          <DocumentSearch
            onResultSelect={(result) => {
              setSelectedResult(result);
              setActiveTab('results');
            }}
          />
        );

      case 'results':
        return selectedResult ? (
          <div className="max-w-4xl mx-auto p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Result Details</h2>

            <div className="bg-white rounded-lg shadow-md p-6">
              {/* Check if it's a Neo4j graph result */}
              {selectedResult.label && selectedResult.group ? (
                <>
                  <div className="mb-4">
                    <h3 className="text-xl font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      {selectedResult.label}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded">Graph Entity</span>
                      <span>Group: {selectedResult.group}</span>
                    </div>
                  </div>

                  {selectedResult.properties && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-700 mb-2">Properties:</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        {Object.entries(selectedResult.properties).map(([key, value]) => (
                          <div key={key} className="mb-2">
                            <span className="font-medium text-gray-700">{key}:</span>
                            <span className="ml-2 text-gray-600">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                /* Document result */
                <>
                  <div className="mb-4">
                    <h3 className="text-xl font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <FileText className="h-5 w-5 text-blue-500" />
                      {selectedResult.id || selectedResult.filename || 'Document Result'}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">Document</span>
                      {selectedResult.type && <span>Type: {selectedResult.type}</span>}
                      {selectedResult.prop_filename && <span>File: {selectedResult.prop_filename}</span>}
                    </div>
                  </div>

                  {selectedResult.content && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-700 mb-2">Content:</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-gray-700 whitespace-pre-wrap">
                          {selectedResult.content.length > 1000
                            ? `${selectedResult.content.substring(0, 1000)}...`
                            : selectedResult.content
                          }
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Display other document properties */}
                  {Object.keys(selectedResult).filter(key =>
                    !['id', 'content', 'type', 'prop_filename'].includes(key) &&
                    selectedResult[key] !== undefined
                  ).length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-700 mb-2">Additional Properties:</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        {Object.entries(selectedResult)
                          .filter(([key]) => !['id', 'content', 'type', 'prop_filename'].includes(key))
                          .map(([key, value]) => (
                            <div key={key} className="mb-2">
                              <span className="font-medium text-gray-700">{key}:</span>
                              <span className="ml-2 text-gray-600">{String(value)}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              <div className="flex gap-4">
                <button
                  onClick={() => setActiveTab('search')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Back to Search
                </button>
                {selectedResult.filename && (
                  <button
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    Analyze Document
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-medium text-gray-600 mb-2">No Result Selected</h3>
            <p className="text-gray-500 mb-4">Search for content to view details here</p>
            <button
              onClick={() => setActiveTab('search')}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Go to Search
            </button>
          </div>
        );

      case 'analytics':
        return (
          <div className="max-w-4xl mx-auto p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Document Analytics</h2>

            {serviceStatus && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Neo4j Database</p>
                      <p className={`text-lg font-semibold ${
                        serviceStatus.neo4j_connection ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {serviceStatus.neo4j_connection ? 'Connected' : 'Disconnected'}
                      </p>
                    </div>
                    <div className={`p-2 rounded-full ${
                      serviceStatus.neo4j_connection ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      <div className={`w-3 h-3 rounded-full ${
                        serviceStatus.neo4j_connection ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Tika Server</p>
                      <p className={`text-lg font-semibold ${
                        serviceStatus.tika_server ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {serviceStatus.tika_server ? 'Running' : 'Stopped'}
                      </p>
                    </div>
                    <div className={`p-2 rounded-full ${
                      serviceStatus.tika_server ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      <div className={`w-3 h-3 rounded-full ${
                        serviceStatus.tika_server ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">LLM Service</p>
                      <p className={`text-lg font-semibold ${
                        serviceStatus.llm_service ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {serviceStatus.llm_service ? 'Running' : 'Stopped'}
                      </p>
                    </div>
                    <div className={`p-2 rounded-full ${
                      serviceStatus.llm_service ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      <div className={`w-3 h-3 rounded-full ${
                        serviceStatus.llm_service ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Available Models</p>
                      <p className="text-lg font-semibold text-blue-600">
                        {serviceStatus.available_models?.length || 0}
                      </p>
                    </div>
                    <div className="p-2 rounded-full bg-blue-100">
                      <Settings className="w-3 h-3 text-blue-500" />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Processed Docs</p>
                      <p className="text-lg font-semibold text-purple-600">
                        {serviceStatus.processed_documents_count || 0}
                      </p>
                    </div>
                    <div className="p-2 rounded-full bg-purple-100">
                      <FileText className="w-3 h-3 text-purple-500" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Supported File Types</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <FileText className="h-8 w-8 mx-auto text-blue-500 mb-2" />
                  <p className="font-medium text-gray-700">Documents</p>
                  <p className="text-sm text-gray-500">PDF, DOCX, TXT</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <FileText className="h-8 w-8 mx-auto text-green-500 mb-2" />
                  <p className="font-medium text-gray-700">Images</p>
                  <p className="text-sm text-gray-500">PNG, JPG, TIFF</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <FileText className="h-8 w-8 mx-auto text-purple-500 mb-2" />
                  <p className="font-medium text-gray-700">Spreadsheets</p>
                  <p className="text-sm text-gray-500">XLSX, CSV</p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Unstructured Data Pipeline
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={checkServiceStatus}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                Refresh Status
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tab Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-1 py-2 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-sm min-h-[600px]">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default UnstructuredDataPage;