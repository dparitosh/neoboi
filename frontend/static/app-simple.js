// Simplified React app using only basic Cytoscape layouts
const { React, ReactDOM } = window;
const { useState, useEffect, useRef, useCallback } = React;

// Use global cytoscape from CDN
const cytoscape = window.cytoscape;

console.log('[App Simple] Using basic Cytoscape layouts only.');

// Enhanced helper function to transform raw graph data to Cytoscape.js element format
function transformDataForCytoscape(graphData) {
    const elements = [];

    if (graphData && graphData.nodes) {
        graphData.nodes.forEach(node => {
            // Enhanced node classification based on properties and labels
            const neo4jLabels = node.group ? [node.group] : ['Unknown'];
            const properties = node.properties || {};
            const name = node.label || properties.name || `Node ${node.id}`;

            // Determine node type for styling - More flexible classification
            let nodeType = 'unknown';
            const labelString = neo4jLabels.join(' ').toLowerCase();
            const nameString = name.toLowerCase();
            const typeString = (properties.type || '').toLowerCase();
            const categoryString = (properties.category || '').toLowerCase();

            // Debug logging to see what data we're working with
            console.log('[Node Classification]', {
                id: node.id,
                label: name,
                group: node.group,
                neo4jLabels: neo4jLabels,
                properties: properties,
                labelString: labelString,
                nameString: nameString,
                typeString: typeString
            });

            // More comprehensive classification logic
            if (labelString.includes('supplier') || nameString.includes('supplier') ||
                typeString.includes('supplier') || categoryString.includes('supplier')) {
                nodeType = 'supplier';
            } else if (labelString.includes('manufacturer') || nameString.includes('manufacturer') ||
                      typeString.includes('manufacturer') || categoryString.includes('manufacturer') ||
                      labelString.includes('factory') || nameString.includes('factory')) {
                nodeType = 'manufacturer';
            } else if (labelString.includes('customer') || nameString.includes('customer') ||
                      typeString.includes('customer') || categoryString.includes('customer') ||
                      labelString.includes('client') || nameString.includes('client')) {
                nodeType = 'customer';
            } else if (labelString.includes('distributor') || nameString.includes('distributor') ||
                      typeString.includes('distributor') || categoryString.includes('distributor')) {
                nodeType = 'distributor';
            } else if (labelString.includes('retailer') || nameString.includes('retailer') ||
                      typeString.includes('retailer') || categoryString.includes('retailer')) {
                nodeType = 'retailer';
            } else if (labelString.includes('warehouse') || nameString.includes('warehouse') ||
                      typeString.includes('warehouse') || categoryString.includes('warehouse') ||
                      labelString.includes('storage') || nameString.includes('storage')) {
                nodeType = 'warehouse';
            } else if (labelString.includes('logistics') || nameString.includes('logistics') ||
                      typeString.includes('logistics') || categoryString.includes('logistics') ||
                      labelString.includes('shipping') || nameString.includes('shipping')) {
                nodeType = 'logistics';
            }

            // Fallback: try to classify based on any property that might indicate type
            if (nodeType === 'unknown') {
                for (const [key, value] of Object.entries(properties)) {
                    const valueStr = String(value).toLowerCase();
                    if (valueStr.includes('supplier') || valueStr.includes('vendor')) {
                        nodeType = 'supplier';
                        break;
                    } else if (valueStr.includes('manufacturer') || valueStr.includes('producer')) {
                        nodeType = 'manufacturer';
                        break;
                    } else if (valueStr.includes('customer') || valueStr.includes('buyer')) {
                        nodeType = 'customer';
                        break;
                    } else if (valueStr.includes('distributor') || valueStr.includes('dealer')) {
                        nodeType = 'distributor';
                        break;
                    }
                }
            }

            console.log('[Node Classification Result]', { id: node.id, nodeType: nodeType });

            // Determine status for additional styling
            let statusClass = '';
            const status = (properties.status || '').toLowerCase();
            if (status.includes('active') || status.includes('online')) {
                statusClass = 'active';
            } else if (status.includes('inactive') || status.includes('offline')) {
                statusClass = 'inactive';
            } else if (status.includes('critical') || status.includes('error')) {
                statusClass = 'critical';
            }

            elements.push({
                group: 'nodes',
                data: {
                    id: String(node.id),
                    label: name,
                    neo4j_labels: neo4jLabels,
                    group: node.group || nodeType,
                    properties: properties,
                    nodeType: nodeType,
                    status: status
                },
                classes: `${nodeType} ${statusClass}`.trim()
            });
        });
    }

    if (graphData && graphData.edges) {
        graphData.edges.forEach(edge => {
            const properties = edge.properties || {};
            const label = edge.label || properties.type || 'RELATIONSHIP';

            // Classify edge type for styling
            let edgeType = '';
            const labelLower = label.toLowerCase();

            if (labelLower.includes('supplies') || labelLower.includes('supply')) {
                edgeType = 'supplies';
            } else if (labelLower.includes('manufactures') || labelLower.includes('manufacture')) {
                edgeType = 'manufactures';
            } else if (labelLower.includes('distributes') || labelLower.includes('distribute')) {
                edgeType = 'distributes';
            } else if (labelLower.includes('sells') || labelLower.includes('sell')) {
                edgeType = 'sells';
            }

            // Check for critical status
            const isCritical = properties.status === 'CRITICAL' ||
                              properties.priority === 'HIGH' ||
                              properties.urgent === true;

            elements.push({
                group: 'edges',
                data: {
                    id: String(edge.id),
                    source: String(edge.from),
                    target: String(edge.to),
                    label: label,
                    properties: properties,
                    edgeType: edgeType
                },
                classes: `${edgeType} ${isCritical ? 'critical' : ''}`.trim()
            });
        });
    }

    console.log('[Transform] Converted elements:', elements.length, 'elements');
    return elements;
}

// Enhanced Corporate Cytoscape Stylesheet with Professional Colors
const cytoscapeStylesheet = [
    // Base node styling - Clean and minimal
    {
        selector: 'node',
        style: {
            'background-color': '#95A5A6', // Light gray as default
            'border-color': '#7F8C8D',
            'border-width': 2,
            'label': 'data(label)',
            'width': 60,
            'height': 60,
            'font-size': '10px',
            'font-family': '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
            'font-weight': '500',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#2C3E50',
            'text-wrap': 'wrap',
            'text-max-width': '50px',
            'text-outline-width': 0,
            'text-background-opacity': 0, // Remove background highlighter
            'shadow-blur': 6,
            'shadow-color': 'rgba(0, 0, 0, 0.15)',
            'shadow-offset-x': 1,
            'shadow-offset-y': 1,
        }
    },

    // Node type specific styling - Corporate color palette
    {
        selector: 'node.supplier',
        style: {
            'background-color': '#27AE60', // Professional green
            'border-color': '#229954',
            'background-gradient-stop-colors': '#27AE60 #2ECC71',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5
        }
    },
    {
        selector: 'node.manufacturer',
        style: {
            'background-color': '#E74C3C', // Professional red
            'border-color': '#C0392B',
            'background-gradient-stop-colors': '#E74C3C #EC7063',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5
        }
    },
    {
        selector: 'node.customer',
        style: {
            'background-color': '#3498DB', // Professional blue
            'border-color': '#2980B9',
            'background-gradient-stop-colors': '#3498DB #5DADE2',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5
        }
    },
    {
        selector: 'node.distributor',
        style: {
            'background-color': '#9B59B6', // Professional purple
            'border-color': '#8E44AD',
            'background-gradient-stop-colors': '#9B59B6 #BB8FCE',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5
        }
    },
    {
        selector: 'node.retailer',
        style: {
            'background-color': '#F39C12', // Professional orange
            'border-color': '#E67E22',
            'background-gradient-stop-colors': '#F39C12 #F8C471',
            'background-gradient-direction': 'radial',
            'color': '#2C3E50',
            'text-outline-color': '#2C3E50',
            'text-outline-width': 0.5
        }
    },
    {
        selector: 'node.warehouse',
        style: {
            'background-color': '#1ABC9C', // Professional teal
            'border-color': '#16A085',
            'background-gradient-stop-colors': '#1ABC9C #48C9B0',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5
        }
    },
    {
        selector: 'node.logistics',
        style: {
            'background-color': '#34495E', // Professional dark blue
            'border-color': '#2C3E50',
            'background-gradient-stop-colors': '#34495E #5D6D7E',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5
        }
    },
    {
        selector: 'node.unknown',
        style: {
            'background-color': '#95A5A6', // Professional gray for unknown types
            'border-color': '#7F8C8D',
            'background-gradient-stop-colors': '#95A5A6 #BDC3C7',
            'background-gradient-direction': 'radial',
            'color': '#2C3E50',
            'text-outline-color': '#2C3E50',
            'text-outline-width': 0.5
        }
    },

    // Status-based styling
    {
        selector: 'node.active',
        style: {
            'border-color': '#27AE60',
            'border-width': 3,
            'shadow-color': 'rgba(39, 174, 96, 0.5)'
        }
    },
    {
        selector: 'node.inactive',
        style: {
            'background-color': '#95A5A6',
            'border-color': '#7F8C8D',
            'opacity': 0.7
        }
    },
    {
        selector: 'node.critical',
        style: {
            'border-color': '#E74C3C',
            'border-width': 4,
            'border-style': 'double',
            'shadow-color': 'rgba(231, 76, 60, 0.6)',
            'shadow-blur': 12
        }
    },

    // Edge styling - Professional and clear
    {
        selector: 'edge',
        style: {
            'width': 2,
            'line-color': '#BDC3C7',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#BDC3C7',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '9px',
            'font-family': '"Segoe UI", Arial, sans-serif',
            'font-weight': '400',
            'color': '#2C3E50',
            'text-background-opacity': 0, // Remove background highlighter
            'text-margin-y': -8,
            'shadow-blur': 2,
            'shadow-color': 'rgba(0, 0, 0, 0.1)',
            'shadow-offset-x': 0.5,
            'shadow-offset-y': 0.5,
        }
    },

    // Relationship type specific styling
    {
        selector: 'edge.supplies',
        style: {
            'line-color': '#27AE60',
            'target-arrow-color': '#27AE60',
            'width': 2.5,
            'line-style': 'solid'
        }
    },
    {
        selector: 'edge.manufactures',
        style: {
            'line-color': '#E74C3C',
            'target-arrow-color': '#E74C3C',
            'width': 2.5,
            'line-style': 'solid'
        }
    },
    {
        selector: 'edge.distributes',
        style: {
            'line-color': '#9B59B6',
            'target-arrow-color': '#9B59B6',
            'width': 2.5,
            'line-style': 'dashed'
        }
    },
    {
        selector: 'edge.sells',
        style: {
            'line-color': '#F39C12',
            'target-arrow-color': '#F39C12',
            'width': 2.5,
            'line-style': 'solid'
        }
    },
    {
        selector: 'edge.critical',
        style: {
            'line-color': '#E74C3C',
            'target-arrow-color': '#E74C3C',
            'width': 3,
            'line-style': 'solid'
        }
    },

    // Selection and interaction states
    {
        selector: 'node:selected',
        style: {
            'border-width': 4,
            'border-color': '#3498db',
            'shadow-blur': 15,
            'shadow-color': 'rgba(52, 152, 219, 0.6)',
            'z-index': 9999
        }
    },
    {
        selector: 'edge:selected',
        style: {
            'width': 4,
            'line-color': '#3498db',
            'shadow-blur': 8,
            'shadow-color': 'rgba(52, 152, 219, 0.6)',
            'z-index': 9999
        }
    },

    // Highlighted elements (for connected nodes/edges)
    {
        selector: '.highlighted',
        style: {
            'border-width': 3,
            'border-color': '#27AE60',
            'background-color': '#2ECC71',
            'shadow-blur': 10,
            'shadow-color': 'rgba(39, 174, 96, 0.5)',
            'z-index': 999,
            'opacity': 1
        }
    },

    // Dimmed elements (non-connected)
    {
        selector: '.dimmed',
        style: {
            'opacity': 0.3,
            'shadow-blur': 2,
            'shadow-color': 'rgba(0, 0, 0, 0.1)'
        }
    },

    // Hover effects
    {
        selector: 'node:hover',
        style: {
            'border-width': 3,
            'shadow-blur': 10,
            'shadow-color': 'rgba(52, 152, 219, 0.4)',
            'z-index': 1000
        }
    },
    {
        selector: 'edge:hover',
        style: {
            'width': 3,
            'shadow-blur': 6,
            'shadow-color': 'rgba(52, 152, 219, 0.4)',
            'z-index': 1000
        }
    }
];

// Simple Cytoscape component using built-in layouts only
function SimpleCytoscapeComponent({ elements, stylesheet, style, onCyReady }) {
    const containerRef = useRef(null);
    const cyRef = useRef(null);

    useEffect(() => {
        if (containerRef.current && !cyRef.current) {
            // Ensure container has proper dimensions
            const container = containerRef.current;
            const rect = container.getBoundingClientRect();
            console.log('[Cytoscape] Container dimensions:', rect.width, 'x', rect.height);
            
            if (rect.width === 0 || rect.height === 0) {
                console.warn('[Cytoscape] Container has zero dimensions, waiting...');
                // Wait a bit and try again
                setTimeout(() => {
                    const newRect = container.getBoundingClientRect();
                    console.log('[Cytoscape] Retrying with dimensions:', newRect.width, 'x', newRect.height);
                    initializeCytoscape(container, elements);
                }, 1000);
                return;
            }
            
            initializeCytoscape(container, elements);
        }
        
        function initializeCytoscape(container, elements) {
            try {
                console.log('[Cytoscape] Initializing with elements:', elements);
                
                // Ensure minimum dimensions
                container.style.minWidth = '400px';
                container.style.minHeight = '400px';
                
                cyRef.current = cytoscape({
                    container: container,
                    elements: elements,
                    style: stylesheet,
                    layout: { 
                        name: 'cose', // Use built-in cose layout instead of fcose
                        animate: true,
                        padding: 30,
                        nodeRepulsion: function(node) { return 8000; },
                        nodeOverlap: 20,
                        idealEdgeLength: function(edge) { return 50; },
                        edgeElasticity: function(edge) { return 100; },
                        nestingFactor: 0.9,
                        gravity: 80,
                        numIter: 1000,
                        initialTemp: 200,
                        coolingFactor: 0.95,
                        minTemp: 1.0
                    }
                });
                
                console.log('[Cytoscape] Instance created, elements count:', cyRef.current.elements().length);
                console.log('[Cytoscape] Nodes:', cyRef.current.nodes().length, 'Edges:', cyRef.current.edges().length);
                
                // If no elements were added, try a simpler layout
                if (cyRef.current.elements().length === 0 && elements.length > 0) {
                    console.warn('[Cytoscape] No elements found, trying grid layout');
                    cyRef.current.add(elements);
                    cyRef.current.layout({ name: 'grid', animate: false }).run();
                }
                
                if (onCyReady) {
                    onCyReady(cyRef.current);
                }
                
                console.log('[App Simple] Cytoscape instance created with cose layout');
            } catch (error) {
                console.error('[App Simple] Error creating Cytoscape instance:', error);
                // Try fallback initialization
                try {
                    console.log('[Cytoscape] Trying fallback initialization');
                    cyRef.current = cytoscape({
                        container: container,
                        elements: elements,
                        style: stylesheet,
                        layout: { name: 'grid' }
                    });
                    console.log('[Cytoscape] Fallback successful');
                } catch (fallbackError) {
                    console.error('[Cytoscape] Fallback also failed:', fallbackError);
                }
            }
        }
    }, []);

    useEffect(() => {
        if (cyRef.current && elements) {
            try {
                console.log('[Cytoscape] Updating elements:', elements.length);
                cyRef.current.elements().remove();
                cyRef.current.add(elements);
                cyRef.current.layout({ 
                    name: 'cose',
                    animate: true,
                    padding: 30,
                    fit: true
                }).run();
                console.log('[Cytoscape] Elements updated, nodes:', cyRef.current.nodes().length, 'edges:', cyRef.current.edges().length);
            } catch (error) {
                console.error('[App Simple] Error updating elements:', error);
            }
        }
    }, [elements]);

    return React.createElement('div', {
        ref: containerRef,
        style: style || { width: '100%', height: '100%' }
    });
}

// Main React App Component
function App() {
    const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
    const [loading, setLoading] = useState(true);
    const [loadingError, setLoadingError] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const [chatInputValue, setChatInputValue] = useState('');
    const [isChatSending, setIsChatSending] = useState(false);
    const [sortColumn, setSortColumn] = useState('label');
    const [sortDirection, setSortDirection] = useState('asc');
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage] = useState(10);
    const [graphChatRatio, setGraphChatRatio] = useState(1); // 1 = equal, >1 = graph larger, <1 = chat larger
    const [topTableRatio, setTopTableRatio] = useState(0.7); // 0.7 = 70% top, 30% table

    const cyRef = useRef(null);
    const chatMessagesRef = useRef(null);
    const [isUserAtBottom, setIsUserAtBottom] = useState(true);
    const [showScrollToBottom, setShowScrollToBottom] = useState(false);

    // Resize handlers
    const [isResizingVertical, setIsResizingVertical] = useState(false);
    const [isResizingHorizontal, setIsResizingHorizontal] = useState(false);

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
            const container = e.currentTarget;
            const rect = container.getBoundingClientRect();
            const ratio = (e.clientX - rect.left) / rect.width;
            setGraphChatRatio(Math.max(0.2, Math.min(0.8, ratio))); // Keep between 20% and 80%
        } else if (isResizingHorizontal) {
            const container = e.currentTarget;
            const rect = container.getBoundingClientRect();
            const ratio = (e.clientY - rect.top) / rect.height;
            setTopTableRatio(Math.max(0.3, Math.min(0.9, ratio))); // Keep between 30% and 90%
        }
    }, [isResizingVertical, isResizingHorizontal]);

    const handleMouseUp = useCallback(() => {
        setIsResizingVertical(false);
        setIsResizingHorizontal(false);
    }, []);

    // Add global mouse event listeners
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

    // Chat scrolling functions
    const scrollToBottom = useCallback(() => {
        if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
            setIsUserAtBottom(true);
            setShowScrollToBottom(false);
        }
    }, []);

    const handleChatScroll = useCallback(() => {
        if (chatMessagesRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = chatMessagesRef.current;
            const atBottom = scrollTop + clientHeight >= scrollHeight - 10; // 10px tolerance
            setIsUserAtBottom(atBottom);
            setShowScrollToBottom(!atBottom && chatMessages.length > 3); // Show button if scrolled up and has messages
        }
    }, [chatMessages.length]);

    // Auto-scroll to bottom when new messages are added
    useEffect(() => {
        if (isUserAtBottom && chatMessagesRef.current) {
            // Small delay to ensure DOM is updated
            setTimeout(() => {
                scrollToBottom();
            }, 100);
        }
    }, [chatMessages, isUserAtBottom, scrollToBottom]);

    // Sorting and pagination functions
    const handleSort = (column) => {
        const direction = sortColumn === column && sortDirection === 'asc' ? 'desc' : 'asc';
        setSortColumn(column);
        setSortDirection(direction);
        setCurrentPage(1); // Reset to first page when sorting
    };

    const getSortedData = () => {
        if (!graphData.nodes) return [];

        return [...graphData.nodes].sort((a, b) => {
            let aValue, bValue;

            switch (sortColumn) {
                case 'type':
                    aValue = a.group || 'Unknown';
                    bValue = b.group || 'Unknown';
                    break;
                case 'label':
                    aValue = a.label || 'Unnamed';
                    bValue = b.label || 'Unnamed';
                    break;
                case 'id':
                    aValue = a.id;
                    bValue = b.id;
                    break;
                case 'connections':
                    aValue = graphData.edges?.filter(edge => edge.from === a.id || edge.to === a.id).length || 0;
                    bValue = graphData.edges?.filter(edge => edge.from === b.id || edge.to === b.id).length || 0;
                    break;
                default:
                    aValue = a.label || 'Unnamed';
                    bValue = b.label || 'Unnamed';
            }

            if (typeof aValue === 'string' && typeof bValue === 'string') {
                aValue = aValue.toLowerCase();
                bValue = bValue.toLowerCase();
            }

            if (sortDirection === 'asc') {
                return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
            } else {
                return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
            }
        });
    };

    const getPaginatedData = () => {
        const sortedData = getSortedData();
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        return sortedData.slice(startIndex, endIndex);
    };

    const getTotalPages = () => {
        return Math.ceil((graphData.nodes?.length || 0) / rowsPerPage);
    };

    const handlePageChange = (page) => {
        setCurrentPage(page);
    };

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
                console.log('[App Simple] Initial graph data fetched:', data);
                console.log('[App Simple] Nodes count:', data.nodes?.length || 0, 'Edges count:', data.edges?.length || 0);
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

    // Chat Logic with dynamic graph updates
    const handleSendChatMessage = async () => {
        if (!chatInputValue.trim()) return;
        const userMessage = chatInputValue.trim();
        setChatMessages(prev => [...prev, { sender: 'You', text: userMessage }]);
        setChatInputValue('');
        setIsChatSending(true);
        
        try {
            // Check for specific commands
            if (userMessage.toLowerCase().includes('refresh') || userMessage.toLowerCase().includes('reload')) {
                // Refresh graph data
                const response = await fetch('/api/graph');
                if (response.ok) {
                    const data = await response.json();
                    setGraphData(data);
                    setChatMessages(prev => [...prev, { sender: 'AI', text: 'Graph data refreshed successfully!' }]);
                } else {
                    throw new Error('Failed to refresh graph data');
                }
            } else if (userMessage.toLowerCase().includes('expand') || userMessage.toLowerCase().includes('more')) {
                // Try to get more nodes/relationships
                const response = await fetch('/api/graph/all');
                if (response.ok) {
                    const data = await response.json();
                    setGraphData(data);
                    setChatMessages(prev => [...prev, { sender: 'AI', text: 'Showing expanded graph with more data!' }]);
                } else {
                    // Fallback to chat API
                    await handleRegularChat(userMessage);
                }
            } else if (userMessage.toLowerCase().includes('filter') || userMessage.toLowerCase().includes('show only')) {
                // Filter functionality
                const filterTerm = userMessage.toLowerCase().replace(/.*?(filter|show only)\s+/g, '');
                const filteredData = {
                    nodes: graphData.nodes.filter(node => 
                        node.label.toLowerCase().includes(filterTerm) || 
                        node.group.toLowerCase().includes(filterTerm)
                    ),
                    edges: graphData.edges.filter(edge => 
                        edge.label.toLowerCase().includes(filterTerm)
                    )
                };
                setGraphData(filteredData);
                setChatMessages(prev => [...prev, { sender: 'AI', text: `Filtered graph to show items containing: "${filterTerm}"` }]);
            } else if (userMessage.toLowerCase().includes('reset') || userMessage.toLowerCase().includes('show all')) {
                // Reset to original data
                const response = await fetch('/api/graph');
                if (response.ok) {
                    const data = await response.json();
                    setGraphData(data);
                    setChatMessages(prev => [...prev, { sender: 'AI', text: 'Reset to original graph data' }]);
                }
            } else {
                // Regular chat with potential graph updates
                await handleRegularChat(userMessage);
            }
        } catch (error) {
            console.error('Error sending message or processing response:', error);
            setChatMessages(prev => [...prev, { sender: 'System', text: `Error: ${error.message}` }]);
        } finally {
            setIsChatSending(false);
        }
    };

    const handleRegularChat = async (userMessage) => {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userMessage })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Chat API error: ${response.status}`);
        }
        
        const llmResponse = await response.json();
        setChatMessages(prev => [...prev, { sender: 'AI', text: llmResponse.textResponse || "Received a response." }]);

        if (llmResponse.graphData && llmResponse.graphData.nodes && llmResponse.graphData.edges) {
            console.log("[App Simple] Received new graph data from chat:", llmResponse.graphData);
            setGraphData(llmResponse.graphData);
        }
    };

    const handleCyReady = (cy) => {
        cyRef.current = cy;
        console.log('[App Simple] Cytoscape instance ready');

        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.id = 'cy-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid #34495E;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            color: #2C3E50;
            max-width: 300px;
            z-index: 10000;
            pointer-events: none;
            display: none;
            backdrop-filter: blur(10px);
        `;
        document.body.appendChild(tooltip);

        // Enhanced tooltip positioning function
        const showTooltip = (event, content) => {
            tooltip.innerHTML = content;
            tooltip.style.display = 'block';

            const cyRect = cy.container().getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();

            let left = event.renderedPosition.x + cyRect.left;
            let top = event.renderedPosition.y + cyRect.top - tooltipRect.height - 10;

            // Adjust if tooltip goes off screen
            if (left + tooltipRect.width > window.innerWidth) {
                left = window.innerWidth - tooltipRect.width - 10;
            }
            if (left < 10) {
                left = 10;
            }
            if (top < 10) {
                top = event.renderedPosition.y + cyRect.top + 20;
            }

            tooltip.style.left = left + 'px';
            tooltip.style.top = top + 'px';
        };

        const hideTooltip = () => {
            tooltip.style.display = 'none';
        };

        // Enhanced node tooltips
        cy.on('mouseover', 'node', function(event) {
            const node = event.target;
            const data = node.data();
            const neo4jLabels = data.neo4j_labels || [];
            const properties = data.properties || {};

            let tooltipContent = `
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #2C3E50;">
                    ${data.label || 'Unnamed Node'}
                </div>
                <div style="margin-bottom: 6px;">
                    <strong>ID:</strong> ${node.id()}
                </div>
            `;

            if (neo4jLabels.length > 0) {
                tooltipContent += `
                    <div style="margin-bottom: 6px;">
                        <strong>Type:</strong> ${neo4jLabels.join(', ')}
                    </div>
                `;
            }

            if (data.group) {
                tooltipContent += `
                    <div style="margin-bottom: 6px;">
                        <strong>Group:</strong> ${data.group}
                    </div>
                `;
            }

            // Show key properties
            const keyProperties = ['name', 'status', 'type', 'category', 'location', 'department'];
            const displayProperties = Object.entries(properties).filter(([key]) =>
                keyProperties.includes(key.toLowerCase()) || key.toLowerCase().includes('name')
            );

            if (displayProperties.length > 0) {
                tooltipContent += `<div style="margin-bottom: 6px;"><strong>Key Properties:</strong></div>`;
                tooltipContent += '<ul style="margin: 0; padding-left: 15px;">';
                displayProperties.slice(0, 5).forEach(([key, value]) => {
                    const displayValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
                    tooltipContent += `<li style="margin-bottom: 2px;"><strong>${key}:</strong> ${displayValue}</li>`;
                });
                if (Object.keys(properties).length > 5) {
                    tooltipContent += `<li style="margin-bottom: 2px;"><em>... and ${Object.keys(properties).length - 5} more</em></li>`;
                }
                tooltipContent += '</ul>';
            }

            // Add connection info
            const connectedEdges = node.connectedEdges();
            const inDegree = node.incomers().length;
            const outDegree = node.outgoers().length;

            tooltipContent += `
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #BDC3C7;">
                    <strong>Connections:</strong> ${connectedEdges.length} (${inDegree} in, ${outDegree} out)
                </div>
            `;

            showTooltip(event, tooltipContent);
        });

        cy.on('mouseout', 'node', hideTooltip);

        // Enhanced edge tooltips
        cy.on('mouseover', 'edge', function(event) {
            const edge = event.target;
            const data = edge.data();
            const properties = data.properties || {};

            let tooltipContent = `
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #2C3E50;">
                    ${data.label || 'Relationship'}
                </div>
                <div style="margin-bottom: 6px;">
                    <strong>ID:</strong> ${edge.id()}
                </div>
                <div style="margin-bottom: 6px;">
                    <strong>From:</strong> ${edge.source().data('label')} (${edge.source().id()})
                </div>
                <div style="margin-bottom: 6px;">
                    <strong>To:</strong> ${edge.target().data('label')} (${edge.target().id()})
                </div>
            `;

            // Show key properties
            const keyProperties = ['weight', 'strength', 'type', 'status', 'created', 'modified'];
            const displayProperties = Object.entries(properties).filter(([key]) =>
                keyProperties.includes(key.toLowerCase())
            );

            if (displayProperties.length > 0) {
                tooltipContent += `<div style="margin-bottom: 6px;"><strong>Properties:</strong></div>`;
                tooltipContent += '<ul style="margin: 0; padding-left: 15px;">';
                displayProperties.forEach(([key, value]) => {
                    const displayValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
                    tooltipContent += `<li style="margin-bottom: 2px;"><strong>${key}:</strong> ${displayValue}</li>`;
                });
                tooltipContent += '</ul>';
            }

            showTooltip(event, tooltipContent);
        });

        cy.on('mouseout', 'edge', hideTooltip);

        // Enhanced click handlers for nodes
        cy.on('tap', 'node', function(event) {
            const node = event.target;
            console.log('Node clicked:', node.id(), node.data());

            // Highlight connected nodes and edges
            const connectedElements = node.connectedEdges().connectedNodes().union(node.connectedEdges());

            // Reset all styles first
            cy.elements().removeClass('highlighted dimmed');

            // Highlight clicked node and connected elements
            node.addClass('highlighted');
            connectedElements.addClass('highlighted');

            // Dim non-connected elements
            cy.elements().not(node).not(connectedElements).addClass('dimmed');

            // Enhanced node info display (disabled)
            // const data = node.data();
            // const neo4jLabels = data.neo4j_labels || [];
            // const properties = data.properties || {};
            // const connectedEdges = node.connectedEdges();
            // const inDegree = node.incomers().length;
            // const outDegree = node.outgoers().length;

            // let nodeInfo = `<strong>${data.label || 'Unnamed Node'}</strong><br/>`;
            // nodeInfo += `ID: ${node.id()}<br/>`;

            // if (neo4jLabels.length > 0) {
            //     nodeInfo += `Type: ${neo4jLabels.join(', ')}<br/>`;
            // }

            // if (data.group) {
            //     nodeInfo += `Group: ${data.group}<br/>`;
            // }

            // nodeInfo += `Connections: ${connectedEdges.length} (${inDegree} in, ${outDegree} out)`;

            // setChatMessages(prev => [...prev, {
            //     sender: 'Graph',
            //     text: nodeInfo,
            //     type: 'node-info'
            // }]);
        });

        // Enhanced click handlers for edges
        cy.on('tap', 'edge', function(event) {
            const edge = event.target;
            console.log('Edge clicked:', edge.id(), edge.data());

            // Highlight edge and connected nodes
            cy.elements().removeClass('highlighted dimmed');
            edge.addClass('highlighted');
            edge.connectedNodes().addClass('highlighted');
            cy.elements().not(edge).not(edge.connectedNodes()).addClass('dimmed');

            // Enhanced edge info display
            const data = edge.data();
            const properties = data.properties || {};

            let edgeInfo = `<strong>${data.label || 'Relationship'}</strong><br/>`;
            edgeInfo += `From: ${edge.source().data('label')} → To: ${edge.target().data('label')}<br/>`;
            edgeInfo += `ID: ${edge.id()}`;

            if (Object.keys(properties).length > 0) {
                edgeInfo += '<br/><strong>Properties:</strong>';
                Object.entries(properties).slice(0, 3).forEach(([key, value]) => {
                    const displayValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
                    edgeInfo += `<br/>• ${key}: ${displayValue}`;
                });
            }

            setChatMessages(prev => [...prev, {
                sender: 'Graph',
                text: edgeInfo,
                type: 'edge-info'
            }]);
        });

        // Double-click to expand/explore node
        cy.on('dblclick', 'node', async function(event) {
            const node = event.target;
            const nodeId = node.id();

            setChatMessages(prev => [...prev, {
                sender: 'Graph',
                text: `<i class="ms-Icon ms-Icon--Search" aria-hidden="true"></i> Exploring connections for: <strong>${node.data('label')}</strong>...`,
                type: 'exploration'
            }]);

            try {
                // Fetch expanded graph data for this node
                const response = await fetch(`/api/graph/expand/${nodeId}`);
                if (response.ok) {
                    const expandedData = await response.json();
                    if (expandedData.nodes && expandedData.edges) {
                        // Merge new data with existing
                        setGraphData(prevData => ({
                            nodes: [...prevData.nodes, ...expandedData.nodes.filter(newNode =>
                                !prevData.nodes.some(existingNode => existingNode.id === newNode.id)
                            )],
                            edges: [...prevData.edges, ...expandedData.edges.filter(newEdge =>
                                !prevData.edges.some(existingEdge => existingEdge.id === newEdge.id)
                            )]
                        }));
                        setChatMessages(prev => [...prev, {
                            sender: 'Graph',
                            text: `<i class="ms-Icon ms-Icon--CheckMark" aria-hidden="true"></i> Added <strong>${expandedData.nodes.length}</strong> new nodes and <strong>${expandedData.edges.length}</strong> new relationships`,
                            type: 'success'
                        }]);
                    }
                } else {
                    setChatMessages(prev => [...prev, {
                        sender: 'Graph',
                        text: `<i class="ms-Icon ms-Icon--Error" aria-hidden="true"></i> No additional connections found for <strong>${node.data('label')}</strong>`,
                        type: 'warning'
                    }]);
                }
            } catch (error) {
                console.error('Error expanding node:', error);
                setChatMessages(prev => [...prev, {
                    sender: 'Graph',
                    text: `<i class="ms-Icon ms-Icon--Error" aria-hidden="true"></i> Error exploring node: ${error.message}`,
                    type: 'error'
                }]);
            }
        });

        // Right-click context menu simulation
        cy.on('cxttap', 'node', function(event) {
            const node = event.target;
            const actions = [
                `<i class="ms-Icon ms-Icon--View" aria-hidden="true"></i> Show details of ${node.data('label')}`,
                `<i class="ms-Icon ms-Icon--Link" aria-hidden="true"></i> Show neighbors of ${node.data('label')}`,
                `<i class="ms-Icon ms-Icon--Analytics" aria-hidden="true"></i> Get properties of ${node.data('label')}`,
                `<i class="ms-Icon ms-Icon--Target" aria-hidden="true"></i> Center on ${node.data('label')}`
            ];

            setChatMessages(prev => [...prev, {
                sender: 'Graph',
                text: `<i class="ms-Icon ms-Icon--List" aria-hidden="true"></i> <strong>Available actions for ${node.data('label')}:</strong><br/>${actions.map(action => `• ${action}`).join('<br/>')}`,
                type: 'actions'
            }]);
        });

        // Click on background to reset highlighting
        cy.on('tap', function(event) {
            if (event.target === cy) {
                cy.elements().removeClass('highlighted dimmed');
                hideTooltip();
            }
        });
    };

    // Show loading or error state
    if (loading) {
        return React.createElement('div', { className: 'loading' }, 'Loading graph data...');
    }

    if (loadingError) {
        return React.createElement('div', { className: 'error' }, 'Error: ', loadingError);
    }

    // Component Return
    return React.createElement('div', { className: 'app' },
        // Page Header
        React.createElement('header', {
            style: {
                background: 'linear-gradient(135deg, #2C3E50 0%, #34495E 100%)',
                color: 'white',
                padding: '16px 24px',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
                borderBottom: '1px solid #BDC3C7',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }
        },
            React.createElement('div', {
                style: { display: 'flex', alignItems: 'center', gap: '12px' }
            },
                React.createElement('h1', {
                    style: {
                        margin: 0,
                        fontSize: '24px',
                        fontWeight: '600',
                        letterSpacing: '-0.5px'
                    }
                }, 'Neo4j Graph Visualization'),
                React.createElement('div', {
                    style: {
                        width: '8px',
                        height: '8px',
                        background: '#27AE60',
                        borderRadius: '50%',
                        boxShadow: '0 0 10px rgba(39, 174, 96, 0.5)'
                    }
                })
            ),
            React.createElement('div', {
                style: {
                    fontSize: '14px',
                    color: '#BDC3C7',
                    fontWeight: '400'
                }
            }, 'Interactive Graph Explorer')
        ),
        React.createElement('div', { className: 'main-content-area' },
            // Top section: Graph and Chat side by side
            React.createElement('div', { 
                className: 'top-section',
                style: { 
                    height: `${topTableRatio * 100}%`, 
                    display: 'flex',
                    position: 'relative'
                }
            },
                React.createElement('div', { 
                    id: 'graph-container',
                    style: { 
                        flex: graphChatRatio, 
                        height: '100%', 
                        position: 'relative',
                        borderRight: '1px solid #BDC3C7'
                    }
                },
                    (() => {
                        const transformedElements = transformDataForCytoscape(graphData);
                        console.log('[App] Rendering Cytoscape with elements:', transformedElements.length);
                        return React.createElement(SimpleCytoscapeComponent, {
                            elements: transformedElements,
                            stylesheet: cytoscapeStylesheet,
                            style: { width: '100%', height: '100%' },
                            onCyReady: handleCyReady
                        });
                    })(),
                    // Enhanced control panel with legend (inside graph container)
                    React.createElement('div', {
                        style: {
                            position: 'absolute',
                            top: '10px',
                            right: '10px',
                            background: 'rgba(255, 255, 255, 0.95)',
                            padding: '10px',
                            borderRadius: '6px',
                            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
                            backdropFilter: 'blur(8px)',
                            border: '1px solid rgba(189, 195, 199, 0.3)',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '6px',
                            zIndex: 1000,
                            maxWidth: '160px',
                            fontSize: '10px'
                        }
                    },
                        // Control buttons (removed)
                        // React.createElement('div', {
                        //     style: { display: 'flex', flexDirection: 'column', gap: '6px' }
                        // },
                        //     React.createElement('button', {
                        //         onClick: async () => {
                        //             try {
                        //                 const response = await fetch('/api/graph');
                        //                 if (response.ok) {
                        //                     const data = await response.json();
                        //                     setGraphData(data);
                        //                     setChatMessages(prev => [...prev, {
                        //                         sender: 'System',
                        //                         text: '<i class="ms-Icon ms-Icon--CheckMark" aria-hidden="true"></i> <strong>Graph refreshed successfully!</strong>',
                        //                         type: 'success'
                        //                     }]);
                        //                 }
                        //             } catch (error) {
                        //                 console.error('Error refreshing:', error);
                        //                 setChatMessages(prev => [...prev, {
                        //                     sender: 'System',
                        //                     text: '<i class="ms-Icon ms-Icon--Error" aria-hidden="true"></i> <strong>Error refreshing graph</strong>',
                        //                     type: 'error'
                        //                 }]);
                        //             }
                        //         },
                        //         style: {
                        //             padding: '8px 12px',
                        //             background: 'linear-gradient(135deg, #27AE60 0%, #2ECC71 100%)',
                        //             color: 'white',
                        //             border: 'none',
                        //             borderRadius: '4px',
                        //             cursor: 'pointer',
                        //             fontSize: '11px',
                        //             fontWeight: '500',
                        //             transition: 'all 0.2s ease'
                        //         },
                        //         onMouseOver: (e) => e.target.style.transform = 'translateY(-1px)',
                        //         onMouseOut: (e) => e.target.style.transform = 'translateY(0)'
                        //     }, React.createElement('span', null,
                        //         React.createElement('i', { className: 'ms-Icon ms-Icon--Refresh', 'aria-hidden': 'true' }),
                        //         ' Refresh'
                        //     )),
                        //     React.createElement('button', {
                        //         onClick: () => {
                        //             if (cyRef.current) {
                        //                 cyRef.current.fit();
                        //                 cyRef.current.center();
                        //             }
                        //         },
                        //         style: {
                        //             padding: '8px 12px',
                        //             background: 'linear-gradient(135deg, #3498DB 0%, #5DADE2 100%)',
                        //             color: 'white',
                        //             border: 'none',
                        //             borderRadius: '4px',
                        //             cursor: 'pointer',
                        //             fontSize: '11px',
                        //             fontWeight: '500',
                        //             transition: 'all 0.2s ease'
                        //         },
                        //         onMouseOver: (e) => e.target.style.transform = 'translateY(-1px)',
                        //         onMouseOut: (e) => e.target.style.transform = 'translateY(0)'
                        //     }, React.createElement('span', null,
                        //         React.createElement('i', { className: 'ms-Icon ms-Icon--Target', 'aria-hidden': 'true' }),
                        //         ' Center'
                        //     )),
                        //     React.createElement('button', {
                        //         onClick: () => {
                        //             if (cyRef.current) {
                        //                 cyRef.current.elements().removeClass('highlighted dimmed');
                        //             }
                        //         },
                        //         style: {
                        //             padding: '8px 12px',
                        //             background: 'linear-gradient(135deg, #E74C3C 0%, #EC7063 100%)',
                        //             color: 'white',
                        //             border: 'none',
                        //             borderRadius: '4px',
                        //             cursor: 'pointer',
                        //             fontSize: '11px',
                        //             fontWeight: '500',
                        //             transition: 'all 0.2s ease'
                        //         },
                        //         onMouseOver: (e) => e.target.style.transform = 'translateY(-1px)',
                        //         onMouseOut: (e) => e.target.style.transform = 'translateY(0)'
                        //     }, React.createElement('span', null,
                        //         React.createElement('i', { className: 'ms-Icon ms-Icon--Clear', 'aria-hidden': 'true' }),
                        //         ' Clear'
                        //     ))
                        // ),

                        // Legend - Dynamic based on actual node types
                        React.createElement('div', {
                            style: {
                                borderTop: '1px solid rgba(189, 195, 199, 0.3)',
                                paddingTop: '12px',
                                fontSize: '10px'
                            }
                        },
                            React.createElement('div', {
                                style: {
                                    fontWeight: '600',
                                    color: '#2C3E50',
                                    marginBottom: '8px',
                                    fontSize: '11px'
                                }
                            }, React.createElement('span', null,
                                React.createElement('i', { className: 'ms-Icon ms-Icon--Color', 'aria-hidden': 'true', style: { marginRight: '4px' } }),
                                'Node Types'
                            )),
                            // Dynamic legend based on actual data
                            (() => {
                                // Get unique node types from current graph data
                                const nodeTypes = new Set();
                                graphData.nodes?.forEach(node => {
                                    const neo4jLabels = node.group ? [node.group] : ['Unknown'];
                                    const properties = node.properties || {};
                                    const name = node.label || properties.name || `Node ${node.id}`;
                                    const labelString = neo4jLabels.join(' ').toLowerCase();
                                    const nameString = name.toLowerCase();
                                    const typeString = (properties.type || '').toLowerCase();
                                    const categoryString = (properties.category || '').toLowerCase();

                                    let detectedType = 'unknown';
                                    if (labelString.includes('supplier') || nameString.includes('supplier') ||
                                        typeString.includes('supplier') || categoryString.includes('supplier')) {
                                        detectedType = 'supplier';
                                    } else if (labelString.includes('manufacturer') || nameString.includes('manufacturer') ||
                                              typeString.includes('manufacturer') || categoryString.includes('manufacturer') ||
                                              labelString.includes('factory') || nameString.includes('factory')) {
                                        detectedType = 'manufacturer';
                                    } else if (labelString.includes('customer') || nameString.includes('customer') ||
                                              typeString.includes('customer') || categoryString.includes('customer') ||
                                              labelString.includes('client') || nameString.includes('client')) {
                                        detectedType = 'customer';
                                    } else if (labelString.includes('distributor') || nameString.includes('distributor') ||
                                              typeString.includes('distributor') || categoryString.includes('distributor')) {
                                        detectedType = 'distributor';
                                    } else if (labelString.includes('retailer') || nameString.includes('retailer') ||
                                              typeString.includes('retailer') || categoryString.includes('retailer')) {
                                        detectedType = 'retailer';
                                    } else if (labelString.includes('warehouse') || nameString.includes('warehouse') ||
                                              typeString.includes('warehouse') || categoryString.includes('warehouse') ||
                                              labelString.includes('storage') || nameString.includes('storage')) {
                                        detectedType = 'warehouse';
                                    } else if (labelString.includes('logistics') || nameString.includes('logistics') ||
                                              typeString.includes('logistics') || categoryString.includes('logistics') ||
                                              labelString.includes('shipping') || nameString.includes('shipping')) {
                                        detectedType = 'logistics';
                                    }

                                    nodeTypes.add(detectedType);
                                });

                                // Define color mapping
                                const colorMap = {
                                    supplier: '#27AE60',
                                    manufacturer: '#E74C3C',
                                    customer: '#3498DB',
                                    distributor: '#9B59B6',
                                    retailer: '#F39C12',
                                    warehouse: '#1ABC9C',
                                    logistics: '#34495E',
                                    unknown: '#95A5A6'
                                };

                                // Define display names
                                const displayNames = {
                                    supplier: 'Supplier',
                                    manufacturer: 'Manufacturer',
                                    customer: 'Customer',
                                    distributor: 'Distributor',
                                    retailer: 'Retailer',
                                    warehouse: 'Warehouse',
                                    logistics: 'Logistics',
                                    unknown: 'Unknown'
                                };

                                // Create legend items for detected types
                                const legendItems = [];
                                nodeTypes.forEach(nodeType => {
                                    legendItems.push(
                                        React.createElement('div', {
                                            key: nodeType,
                                            style: { display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }
                                        },
                                            React.createElement('div', {
                                                style: {
                                                    width: '8px',
                                                    height: '8px',
                                                    background: colorMap[nodeType] || '#95A5A6',
                                                    borderRadius: '50%'
                                                }
                                            }),
                                            React.createElement('span', {
                                                style: { color: '#2C3E50', fontSize: '9px' }
                                            }, displayNames[nodeType] || nodeType)
                                        )
                                    );
                                });

                                return legendItems;
                            })(),

                            // Stats
                            React.createElement('div', {
                                style: {
                                    fontSize: '9px',
                                    color: '#7F8C8D',
                                    textAlign: 'center',
                                    fontWeight: '500',
                                    marginTop: '8px',
                                    paddingTop: '8px',
                                    borderTop: '1px solid rgba(189, 195, 199, 0.3)'
                                }
                            },
                                `Nodes: ${graphData.nodes?.length || 0}`,
                                React.createElement('br'),
                                `Edges: ${graphData.edges?.length || 0}`
                            )
                        )
                    )
                ),
                React.createElement('div', { 
                    id: 'graph-chat-resizer',
                    className: 'resizer-vertical',
                    style: {
                        width: '4px',
                        background: '#BDC3C7',
                        cursor: 'col-resize',
                        opacity: 0.7,
                        transition: 'opacity 0.2s ease'
                    },
                    onMouseDown: handleMouseDownVertical,
                    onMouseOver: (e) => e.target.style.opacity = '1',
                    onMouseOut: (e) => e.target.style.opacity = '0.7'
                }),
                React.createElement('div', { 
                    className: 'chat-panels-container',
                    style: { 
                        flex: 1 - graphChatRatio, 
                        display: 'flex', 
                        flexDirection: 'column',
                        borderLeft: '1px solid #BDC3C7'
                    }
                },
                    React.createElement('div', { 
                        className: 'chat-section',
                        style: { 
                            display: 'flex', 
                            flexDirection: 'column', 
                            height: '100%',
                            background: '#fafafa',
                            borderRadius: '6px',
                            overflow: 'hidden',
                            position: 'relative' // For absolute positioning of scroll button
                        }
                    },
                        React.createElement('div', { 
                            className: 'chat-messages',
                            ref: chatMessagesRef,
                            style: { 
                                flex: '1', 
                                overflowY: 'auto', 
                                padding: '8px', 
                                border: 'none',
                                background: 'transparent',
                                maxHeight: 'calc(100% - 60px)', // Leave space for input
                                scrollBehavior: 'smooth'
                            },
                            onScroll: handleChatScroll
                        },
                            chatMessages.length === 0 ? 
                                React.createElement('div', { style: { color: '#666', fontStyle: 'italic' } }, 
                                    'Welcome! Try these commands:',
                                    React.createElement('br'),
                                    '• "show suppliers" - Display suppliers',
                                    React.createElement('br'),
                                    '• "count nodes" - Get statistics',
                                    React.createElement('br'),
                                    '• "refresh" - Reload data',
                                    React.createElement('br'),
                                    '• "help" - See all commands',
                                    React.createElement('br'),
                                    'Or click/double-click nodes in the graph!'
                                ) :
                                chatMessages.map((msg, index) =>
                                    React.createElement('div', { 
                                        key: index, 
                                        className: 'chat-message',
                                        style: { 
                                            marginBottom: '8px',
                                            padding: '5px',
                                            backgroundColor: msg.sender === 'You' ? '#e3f2fd' : 
                                                            msg.sender === 'System' ? '#fff3e0' :
                                                            msg.sender === 'Graph' ? '#f3e5f5' : '#f5f5f5',
                                            borderRadius: '3px'
                                        }
                                    },
                                        React.createElement('strong', null, msg.sender + ': '),
                                        msg.text
                                    )
                                )
                        ),
                        // Scroll to bottom button
                        showScrollToBottom && React.createElement('button', {
                            onClick: scrollToBottom,
                            style: {
                                position: 'absolute',
                                bottom: '70px',
                                right: '10px',
                                width: '32px',
                                height: '32px',
                                borderRadius: '50%',
                                background: '#3498db',
                                color: 'white',
                                border: 'none',
                                cursor: 'pointer',
                                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '14px',
                                zIndex: 100,
                                transition: 'all 0.2s ease'
                            },
                            onMouseOver: (e) => e.target.style.transform = 'scale(1.1)',
                            onMouseOut: (e) => e.target.style.transform = 'scale(1)',
                            title: 'Scroll to bottom'
                        }, '↓'),
                        React.createElement('div', { 
                            className: 'chat-input',
                            style: { 
                                padding: '8px', 
                                display: 'flex', 
                                gap: '8px',
                                background: '#f0f0f0',
                                borderTop: '1px solid #ddd',
                                flexShrink: 0
                            }
                        },
                            React.createElement('input', {
                                type: 'text',
                                value: chatInputValue,
                                onChange: (e) => setChatInputValue(e.target.value),
                                onKeyPress: (e) => e.key === 'Enter' && handleSendChatMessage(),
                                placeholder: 'Ask about the graph...',
                                disabled: isChatSending,
                                style: { 
                                    flex: '1', 
                                    padding: '6px 8px',
                                    border: '1px solid #ccc',
                                    borderRadius: '4px',
                                    fontSize: '12px'
                                }
                            }),
                            React.createElement('button', {
                                onClick: handleSendChatMessage,
                                disabled: isChatSending,
                                style: { 
                                    padding: '6px 12px',
                                    background: '#3498db',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    fontSize: '12px',
                                    fontWeight: '500'
                                }
                            }, isChatSending ? '...' : 'Send')
                        )
                    )
                )
            ),
            // Horizontal resizer between top section and data table
            React.createElement('div', { 
                id: 'top-table-resizer',
                className: 'resizer-horizontal',
                style: {
                    height: '4px',
                    background: '#BDC3C7',
                    cursor: 'row-resize',
                    opacity: 0.7,
                    transition: 'opacity 0.2s ease'
                },
                onMouseDown: handleMouseDownHorizontal,
                onMouseOver: (e) => e.target.style.opacity = '1',
                onMouseOut: (e) => e.target.style.opacity = '0.7'
            }),
            // Bottom section: Data table
            React.createElement('div', { id: 'main-resizer-v', className: 'resizer-vertical' }),
            React.createElement('div', { 
                className: 'data-table-container',
                style: { 
                    height: `${(1 - topTableRatio) * 100}%`,
                    borderTop: '1px solid #BDC3C7' 
                }
            },
                React.createElement('div', { className: 'data-table-section' },
                    React.createElement('h3', { style: { margin: '0 0 16px 0', color: '#2C3E50' } }, 'Graph Data Table'),
                    React.createElement('div', { className: 'data-table' },
                        React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
                            React.createElement('thead', null,
                                React.createElement('tr', null,
                                    React.createElement('th', {
                                        style: {
                                            padding: '8px',
                                            border: '1px solid #ddd',
                                            background: '#f5f5f5',
                                            textAlign: 'left',
                                            cursor: 'pointer',
                                            userSelect: 'none'
                                        },
                                        onClick: () => handleSort('type')
                                    },
                                        'Type ',
                                        sortColumn === 'type' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'
                                    ),
                                    React.createElement('th', {
                                        style: {
                                            padding: '8px',
                                            border: '1px solid #ddd',
                                            background: '#f5f5f5',
                                            textAlign: 'left',
                                            cursor: 'pointer',
                                            userSelect: 'none'
                                        },
                                        onClick: () => handleSort('label')
                                    },
                                        'Label ',
                                        sortColumn === 'label' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'
                                    ),
                                    React.createElement('th', {
                                        style: {
                                            padding: '8px',
                                            border: '1px solid #ddd',
                                            background: '#f5f5f5',
                                            textAlign: 'left',
                                            cursor: 'pointer',
                                            userSelect: 'none'
                                        },
                                        onClick: () => handleSort('id')
                                    },
                                        'ID ',
                                        sortColumn === 'id' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'
                                    ),
                                    React.createElement('th', {
                                        style: {
                                            padding: '8px',
                                            border: '1px solid #ddd',
                                            background: '#f5f5f5',
                                            textAlign: 'left',
                                            cursor: 'pointer',
                                            userSelect: 'none'
                                        },
                                        onClick: () => handleSort('connections')
                                    },
                                        'Connections ',
                                        sortColumn === 'connections' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'
                                    )
                                )
                            ),
                            React.createElement('tbody', null,
                                getPaginatedData().map((node, index) =>
                                    React.createElement('tr', { key: index },
                                        React.createElement('td', { style: { padding: '8px', border: '1px solid #ddd' } }, node.group || 'Unknown'),
                                        React.createElement('td', { style: { padding: '8px', border: '1px solid #ddd' } }, node.label || 'Unnamed'),
                                        React.createElement('td', { style: { padding: '8px', border: '1px solid #ddd' } }, node.id),
                                        React.createElement('td', { style: { padding: '8px', border: '1px solid #ddd' } },
                                            graphData.edges?.filter(edge => edge.from === node.id || edge.to === node.id).length || 0
                                        )
                                    )
                                )
                            )
                        ),
                        // Pagination controls
                        React.createElement('div', {
                            style: {
                                marginTop: '16px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '8px',
                                background: '#f9f9f9',
                                borderRadius: '4px'
                            }
                        },
                            React.createElement('div', {
                                style: { fontSize: '14px', color: '#666' }
                            },
                                `Showing ${Math.min((currentPage - 1) * rowsPerPage + 1, graphData.nodes?.length || 0)} to ${Math.min(currentPage * rowsPerPage, graphData.nodes?.length || 0)} of ${graphData.nodes?.length || 0} nodes`
                            ),
                            React.createElement('div', {
                                style: { display: 'flex', gap: '8px', alignItems: 'center' }
                            },
                                React.createElement('button', {
                                    onClick: () => handlePageChange(currentPage - 1),
                                    disabled: currentPage === 1,
                                    style: {
                                        padding: '6px 12px',
                                        background: currentPage === 1 ? '#ccc' : '#3498db',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                                        fontSize: '12px'
                                    }
                                }, 'Previous'),
                                React.createElement('span', {
                                    style: { fontSize: '14px', color: '#666', margin: '0 8px' }
                                },
                                    `Page ${currentPage} of ${getTotalPages()}`
                                ),
                                React.createElement('button', {
                                    onClick: () => handlePageChange(currentPage + 1),
                                    disabled: currentPage === getTotalPages(),
                                    style: {
                                        padding: '6px 12px',
                                        background: currentPage === getTotalPages() ? '#ccc' : '#3498db',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: currentPage === getTotalPages() ? 'not-allowed' : 'pointer',
                                        fontSize: '12px'
                                    }
                                }, 'Next')
                            )
                        )
                    )
                )
            )
        )
    );
}

// Mount the React app to the DOM
document.addEventListener('DOMContentLoaded', () => {
    const rootElement = document.getElementById('root');
    if (rootElement) {
        const root = ReactDOM.createRoot(rootElement);
        root.render(React.createElement(App));
        console.log('[App Simple] Application mounted successfully');
    } else {
        console.error('[App Simple] Root element not found');
    }
});
