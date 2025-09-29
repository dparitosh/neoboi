import React, { useState, useEffect, useCallback } from 'react';
import GraphVisualization from '../visualization/GraphVisualization.jsx';
import ErrorDisplay from '../common/ErrorDisplay.jsx';
import LoadingSpinner from '../common/LoadingSpinner.jsx';
import { Upload, ChevronDown, ChevronUp, X } from 'lucide-react';

const GraphContainer = ({ graphData, loading, error, onNodeSelect }) => {
    const [selectedNode, setSelectedNode] = useState(null);

    const handleNodeSelect = useCallback((nodeData) => {
        console.log('[GraphContainer] Node selected:', nodeData);
        setSelectedNode(nodeData);
        if (onNodeSelect) {
            onNodeSelect(nodeData);
        }
    }, [onNodeSelect]);

    if (error) {
        return (
            <div className="p-10 text-center text-red-600 bg-white border-2 border-red-600 rounded-lg m-5">
                <h3 className="font-bold text-lg">Error Loading Graph Data</h3>
                <p>{error}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="mt-3 px-4 py-2 bg-red-600 text-white border-none rounded-md cursor-pointer"
                >
                    Reload Page
                </button>
            </div>
        );
    }

    return (
        <div className="w-full h-full flex flex-col bg-gray-100 font-sans">
            <div className="flex-grow bg-white m-2 rounded-lg shadow-md flex flex-col p-4">
                <div className="mb-4 flex justify-between items-center">
                    <h2 className="m-0 text-gray-800 text-xl font-semibold">
                        Knowledge Graph
                    </h2>
                    {selectedNode && (
                        <div className="px-3 py-2 bg-blue-100 border border-blue-400 rounded-md text-xs text-blue-700">
                            Selected: {selectedNode.label}
                        </div>
                    )}
                </div>
                <div className="flex-grow">
                    <GraphVisualization
                        graphData={graphData}
                        onNodeSelect={handleNodeSelect}
                        loading={loading}
                    />
                </div>
            </div>
        </div>
    );
};

export default GraphContainer;