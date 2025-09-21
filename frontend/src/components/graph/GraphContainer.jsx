import React, { useState, useEffect, useCallback } from 'react';
import GraphVisualization from '../visualization/GraphVisualization.jsx';
import ChatInterface from '../chat/ChatInterface.jsx';
import DataTable from '../table/DataTable.jsx';
import { Upload, X, ChevronDown, ChevronUp } from 'lucide-react';

const GraphContainer = () => {
    const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
    const [loading, setLoading] = useState(true);
    const [loadingError, setLoadingError] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    
    // File upload state
    const [showUploadPanel, setShowUploadPanel] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState(false);
    const [uploadProgress, setUploadProgress] = useState([]);
    const [uploadResults, setUploadResults] = useState([]);
    
    // Layout ratios for resizable panels
    const [graphChatRatio, setGraphChatRatio] = useState(0.6); // 60% graph, 40% chat
    const [topTableRatio, setTopTableRatio] = useState(0.7); // 70% top (graph+chat), 30% table

    // Resize handlers
    const [isResizingVertical, setIsResizingVertical] = useState(false);
    const [isResizingHorizontal, setIsResizingHorizontal] = useState(false);

    // Fetch Initial Graph Data
    useEffect(() => {
        async function fetchInitialData() {
            setLoading(true);
            setLoadingError(null);
            try {
                const response = await fetch('/api/graph');
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log('[GraphContainer] Initial graph data fetched:', data);
                console.log('[GraphContainer] Nodes count:', data.nodes?.length || 0, 'Edges count:', data.edges?.length || 0);
                setGraphData(data);
            } catch (error) {
                console.error('Failed to fetch graph data:', error);
                setLoadingError(`Error loading graph: ${error.message}. Check console for details.`);
            } finally {
                setLoading(false);
            }
        }
        fetchInitialData();
    }, []);

    // Handle graph updates from chat
    const handleGraphUpdate = useCallback((newGraphData) => {
        console.log('[GraphContainer] Updating graph data from chat:', newGraphData);
        setGraphData(newGraphData);
    }, []);

    // Handle node selection from graph
    const handleNodeSelect = useCallback((nodeData) => {
        console.log('[GraphContainer] Node selected:', nodeData);
        setSelectedNode(nodeData);
    }, []);

    // File upload handlers
    const handleFileUpload = async (files) => {
        if (files.length === 0) return;

        setUploadingFiles(true);
        setUploadProgress([]);
        setUploadResults([]);

        try {
            const formData = new FormData();
            files.forEach((file, index) => {
                formData.append('files', file);
            });

            // Initialize progress for each file
            const progressItems = files.map(file => ({
                filename: file.name,
                size: file.size,
                status: 'uploading',
                progress: 0
            }));
            setUploadProgress(progressItems);

            const response = await fetch('/api/unstructured/batch-process', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (result.success) {
                // Update progress to completed
                setUploadProgress(prev => prev.map(item => ({
                    ...item,
                    status: 'completed',
                    progress: 100
                })));

                setUploadResults([{
                    success: true,
                    message: `Successfully processed ${result.files?.length || 0} files`,
                    files: result.files
                }]);

                // Refresh graph data after successful upload
                setTimeout(async () => {
                    try {
                        const graphResponse = await fetch('/api/graph');
                        if (graphResponse.ok) {
                            const newGraphData = await graphResponse.json();
                            setGraphData(newGraphData);
                            console.log('[GraphContainer] Graph refreshed after file upload');
                        }
                    } catch (error) {
                        console.error('Failed to refresh graph after upload:', error);
                    }
                }, 2000); // Wait 2 seconds for processing to complete

            } else {
                setUploadProgress(prev => prev.map(item => ({
                    ...item,
                    status: 'error',
                    progress: 0
                })));
                setUploadResults([{
                    success: false,
                    message: result.error || 'Upload failed'
                }]);
            }
        } catch (error) {
            console.error('Upload error:', error);
            setUploadProgress(prev => prev.map(item => ({
                ...item,
                status: 'error',
                progress: 0
            })));
            setUploadResults([{
                success: false,
                message: 'Network error occurred during upload'
            }]);
        } finally {
            setUploadingFiles(false);
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Resize handlers
    const handleMouseDownVertical = (e) => {
        setIsResizingVertical(true);
        e.preventDefault();
    };

    const handleMouseDownHorizontal = (e) => {
        setIsResizingHorizontal(true);
        e.preventDefault();
    };

    const handleMouseMove = useCallback((e) => {
        if (isResizingVertical) {
            const container = document.getElementById('main-container');
            if (container) {
                const rect = container.getBoundingClientRect();
                const ratio = (e.clientX - rect.left) / rect.width;
                setGraphChatRatio(Math.max(0.2, Math.min(0.8, ratio))); // Keep between 20% and 80%
            }
        } else if (isResizingHorizontal) {
            const container = document.getElementById('main-container');
            if (container) {
                const rect = container.getBoundingClientRect();
                const ratio = (e.clientY - rect.top) / rect.height;
                setTopTableRatio(Math.max(0.3, Math.min(0.9, ratio))); // Keep between 30% and 90%
            }
        }
    }, [isResizingVertical, isResizingHorizontal]);

    const handleMouseUp = useCallback(() => {
        setIsResizingVertical(false);
        setIsResizingHorizontal(false);
    }, []);

    // Add global mouse event listeners for resizing
    useEffect(() => {
        if (isResizingVertical || isResizingHorizontal) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            return () => {
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            };
        }
    }, [isResizingVertical, isResizingHorizontal, handleMouseMove, handleMouseUp]);

    if (loadingError) {
        return (
            <div style={{
                padding: '40px',
                textAlign: 'center',
                color: '#E74C3C',
                background: '#FFFFFF',
                border: '2px solid #E74C3C',
                borderRadius: '8px',
                margin: '20px'
            }}>
                <h3>Error Loading Graph Data</h3>
                <p>{loadingError}</p>
                <button 
                    onClick={() => window.location.reload()}
                    style={{
                        padding: '10px 20px',
                        background: '#E74C3C',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        marginTop: '10px'
                    }}
                >
                    Reload Page
                </button>
            </div>
        );
    }

    return (
        <div 
            id="main-container"
            style={{
                width: '100vw',
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                background: '#ECF0F1',
                fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
                overflow: 'hidden'
            }}
        >
            {/* File Upload Panel */}
            {showUploadPanel && (
                <div style={{
                    background: '#FFFFFF',
                    margin: '8px',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    border: '1px solid #BDC3C7'
                }}>
                    <div style={{
                        padding: '16px',
                        borderBottom: '1px solid #BDC3C7',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        background: '#F8F9FA',
                        borderRadius: '8px 8px 0 0'
                    }}>
                        <h3 style={{
                            margin: 0,
                            color: '#2C3E50',
                            fontSize: '16px',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}>
                            <Upload size={18} />
                            Document Upload
                        </h3>
                        <button
                            onClick={() => setShowUploadPanel(false)}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: '#7F8C8D',
                                cursor: 'pointer',
                                padding: '4px',
                                borderRadius: '4px'
                            }}
                        >
                            <X size={16} />
                        </button>
                    </div>

                    <div style={{ padding: '16px' }}>
                        {/* Drag & Drop Area */}
                        <div
                            style={{
                                border: '2px dashed #BDC3C7',
                                borderRadius: '8px',
                                padding: '40px 20px',
                                textAlign: 'center',
                                background: '#FAFAFA',
                                marginBottom: '16px',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                            onDragOver={(e) => {
                                e.preventDefault();
                                e.currentTarget.style.borderColor = '#3498DB';
                                e.currentTarget.style.background = '#EBF5FB';
                            }}
                            onDragLeave={(e) => {
                                e.preventDefault();
                                e.currentTarget.style.borderColor = '#BDC3C7';
                                e.currentTarget.style.background = '#FAFAFA';
                            }}
                            onDrop={(e) => {
                                e.preventDefault();
                                e.currentTarget.style.borderColor = '#BDC3C7';
                                e.currentTarget.style.background = '#FAFAFA';

                                const files = Array.from(e.dataTransfer.files);
                                if (files.length > 0) {
                                    handleFileUpload(files);
                                }
                            }}
                            onClick={() => document.getElementById('file-input')?.click()}
                        >
                            <Upload size={32} style={{ color: '#BDC3C7', marginBottom: '12px' }} />
                            <div style={{ fontSize: '16px', fontWeight: '500', color: '#2C3E50', marginBottom: '4px' }}>
                                Drop files here or click to browse
                            </div>
                            <div style={{ fontSize: '14px', color: '#7F8C8D' }}>
                                Supports PDF, DOCX, TXT, PNG, JPG, JPEG (max 50MB each)
                            </div>
                            <input
                                id="file-input"
                                type="file"
                                multiple
                                accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                                style={{ display: 'none' }}
                                onChange={(e) => {
                                    const files = Array.from(e.target.files || []);
                                    if (files.length > 0) {
                                        handleFileUpload(files);
                                    }
                                    e.target.value = ''; // Reset input
                                }}
                            />
                        </div>

                        {/* Upload Progress */}
                        {uploadProgress.length > 0 && (
                            <div style={{ marginBottom: '16px' }}>
                                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#2C3E50', marginBottom: '8px' }}>
                                    Upload Progress
                                </h4>
                                <div style={{ spaceY: '8px' }}>
                                    {uploadProgress.map((item, index) => (
                                        <div key={index} style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '12px',
                                            padding: '8px',
                                            background: '#F8F9FA',
                                            borderRadius: '6px',
                                            border: '1px solid #E9ECEF'
                                        }}>
                                            <div style={{
                                                width: '20px',
                                                height: '20px',
                                                borderRadius: '50%',
                                                background: item.status === 'completed' ? '#27AE60' :
                                                           item.status === 'error' ? '#E74C3C' : '#3498DB',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                {item.status === 'completed' && <span style={{ color: 'white', fontSize: '12px' }}>✓</span>}
                                                {item.status === 'error' && <span style={{ color: 'white', fontSize: '12px' }}>✗</span>}
                                                {item.status === 'uploading' && <div style={{
                                                    width: '8px',
                                                    height: '8px',
                                                    background: 'white',
                                                    borderRadius: '50%',
                                                    animation: 'pulse 1s infinite'
                                                }}></div>}
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontSize: '14px', fontWeight: '500', color: '#2C3E50' }}>
                                                    {item.filename}
                                                </div>
                                                <div style={{ fontSize: '12px', color: '#7F8C8D' }}>
                                                    {formatFileSize(item.size)}
                                                </div>
                                            </div>
                                            <div style={{ fontSize: '12px', color: '#7F8C8D' }}>
                                                {item.status === 'completed' && 'Completed'}
                                                {item.status === 'error' && 'Failed'}
                                                {item.status === 'uploading' && 'Processing...'}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Upload Results */}
                        {uploadResults.length > 0 && (
                            <div>
                                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#2C3E50', marginBottom: '8px' }}>
                                    Upload Results
                                </h4>
                                {uploadResults.map((result, index) => (
                                    <div key={index} style={{
                                        padding: '12px',
                                        borderRadius: '6px',
                                        background: result.success ? '#D4EDDA' : '#F8D7DA',
                                        border: `1px solid ${result.success ? '#C3E6CB' : '#F5C6CB'}`,
                                        color: result.success ? '#155724' : '#721C24'
                                    }}>
                                        <div style={{ fontWeight: '500', marginBottom: '4px' }}>
                                            {result.success ? '✓ Success' : '✗ Error'}
                                        </div>
                                        <div style={{ fontSize: '14px' }}>
                                            {result.message}
                                        </div>
                                        {result.files && (
                                            <div style={{ fontSize: '12px', marginTop: '4px', opacity: 0.8 }}>
                                                Files processed: {result.files.join(', ')}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Top Section: Graph + Chat */}
            <div style={{
                height: `${topTableRatio * 100}%`,
                display: 'flex',
                background: '#FFFFFF',
                margin: '8px',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
                {/* Graph Section */}
                <div style={{
                    width: `${graphChatRatio * 100}%`,
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column'
                }}>
                    <div style={{
                        marginBottom: '16px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <h2 style={{ 
                            margin: 0, 
                            color: '#2C3E50',
                            fontSize: '20px',
                            fontWeight: '600'
                        }}>
                            Knowledge Graph
                        </h2>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <button
                                onClick={() => setShowUploadPanel(!showUploadPanel)}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    padding: '8px 12px',
                                    background: showUploadPanel ? '#E8F4FD' : '#F8F9FA',
                                    border: `1px solid ${showUploadPanel ? '#3498DB' : '#BDC3C7'}`,
                                    borderRadius: '6px',
                                    color: showUploadPanel ? '#2980B9' : '#2C3E50',
                                    fontSize: '14px',
                                    fontWeight: '500',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <Upload size={16} />
                                Upload Files
                                {showUploadPanel ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                            </button>
                            {selectedNode && (
                                <div style={{
                                    padding: '8px 12px',
                                    background: '#E8F4FD',
                                    border: '1px solid #3498DB',
                                    borderRadius: '6px',
                                    fontSize: '12px',
                                    color: '#2980B9'
                                }}>
                                    Selected: {selectedNode.label}
                                </div>
                            )}
                        </div>
                    </div>
                    <div style={{ flex: 1 }}>
                        <GraphVisualization
                            graphData={graphData}
                            onNodeSelect={handleNodeSelect}
                            loading={loading}
                        />
                    </div>
                </div>

                {/* Vertical Resize Handle */}
                <div
                    onMouseDown={handleMouseDownVertical}
                    style={{
                        width: '4px',
                        cursor: 'col-resize',
                        backgroundColor: isResizingVertical ? '#3498DB' : '#BDC3C7',
                        transition: 'background-color 0.2s',
                        margin: '16px 0',
                        borderRadius: '2px'
                    }}
                />

                {/* Chat Section */}
                <div style={{
                    width: `${(1 - graphChatRatio) * 100}%`,
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column'
                }}>
                    <div style={{ flex: 1 }}>
                        <ChatInterface
                            onGraphUpdate={handleGraphUpdate}
                            loading={loading}
                        />
                    </div>
                </div>
            </div>

            {/* Horizontal Resize Handle */}
            <div
                onMouseDown={handleMouseDownHorizontal}
                style={{
                    height: '4px',
                    cursor: 'row-resize',
                    backgroundColor: isResizingHorizontal ? '#3498DB' : '#BDC3C7',
                    transition: 'background-color 0.2s',
                    margin: '0 16px',
                    borderRadius: '2px'
                }}
            />

            {/* Bottom Section: Data Table */}
            <div style={{
                height: `${(1 - topTableRatio) * 100}%`,
                background: '#FFFFFF',
                margin: '8px',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column'
            }}>
                <div style={{ flex: 1 }}>
                    <DataTable
                        graphData={graphData}
                        loading={loading}
                    />
                </div>
            </div>
        </div>
    );
};

<style jsx>{`
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
`}</style>

export default GraphContainer;
