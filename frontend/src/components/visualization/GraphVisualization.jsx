import React, { useRef, useEffect, useState } from 'react';

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

// Enhanced Corporate Cytoscape Stylesheet with Professional Colors and Improved Tooltips
const cytoscapeStylesheet = [
    // Base node styling - Clean and minimal with enhanced shadows
    {
        selector: 'node',
        style: {
            'background-color': '#95A5A6',
            'border-color': '#7F8C8D',
            'border-width': 2,
            'label': 'data(label)',
            'width': 65,
            'height': 65,
            'font-size': '11px',
            'font-family': '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
            'font-weight': '600',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#2C3E50',
            'text-wrap': 'wrap',
            'text-max-width': '55px',
            'text-outline-width': 0,
            'text-background-opacity': 0,
            'shadow-blur': 8,
            'shadow-color': 'rgba(0, 0, 0, 0.2)',
            'shadow-offset-x': 2,
            'shadow-offset-y': 2,
            'transition-property': 'border-width, shadow-blur, background-color',
            'transition-duration': '0.2s'
        }
    },

    // Enhanced Node type specific styling - Vibrant corporate color palette with gradients
    {
        selector: 'node.supplier',
        style: {
            'background-color': '#27AE60',
            'border-color': '#229954',
            'background-gradient-stop-colors': '#27AE60 #2ECC71 #27AE60',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5,
            'shape': 'ellipse'
        }
    },
    {
        selector: 'node.manufacturer',
        style: {
            'background-color': '#3498DB',
            'border-color': '#2980B9',
            'background-gradient-stop-colors': '#3498DB #5DADE2 #3498DB',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5,
            'shape': 'round-rectangle'
        }
    },
    {
        selector: 'node.customer',
        style: {
            'background-color': '#E74C3C',
            'border-color': '#C0392B',
            'background-gradient-stop-colors': '#E74C3C #EC7063 #E74C3C',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5,
            'shape': 'diamond'
        }
    },
    {
        selector: 'node.distributor',
        style: {
            'background-color': '#F39C12',
            'border-color': '#E67E22',
            'background-gradient-stop-colors': '#F39C12 #F7DC6F #F39C12',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5,
            'shape': 'hexagon'
        }
    },
    {
        selector: 'node.retailer',
        style: {
            'background-color': '#9B59B6',
            'border-color': '#8E44AD',
            'background-gradient-stop-colors': '#9B59B6 #BB8FCE #9B59B6',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5,
            'shape': 'star'
        }
    },
    {
        selector: 'node.warehouse',
        style: {
            'background-color': '#16A085',
            'border-color': '#138D75',
            'background-gradient-stop-colors': '#16A085 #48C9B0 #16A085',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5,
            'shape': 'round-triangle'
        }
    },
    {
        selector: 'node.logistics',
        style: {
            'background-color': '#D35400',
            'border-color': '#BA4A00',
            'background-gradient-stop-colors': '#D35400 #E67E22 #D35400',
            'background-gradient-direction': 'radial',
            'color': '#FFFFFF',
            'text-outline-color': '#FFFFFF',
            'text-outline-width': 0.5,
            'shape': 'vee'
        }
    },

    // Enhanced Status-based styling overlays with pulsing effects
    {
        selector: 'node.active',
        style: {
            'border-width': 4,
            'border-color': '#2ECC71',
            'shadow-blur': 12,
            'shadow-color': 'rgba(46, 204, 113, 0.6)',
            'background-gradient-stop-colors': '#27AE60 #52D17B #27AE60'
        }
    },
    {
        selector: 'node.inactive',
        style: {
            'opacity': 0.7,
            'border-style': 'dashed',
            'border-color': '#95A5A6',
            'background-gradient-stop-colors': '#95A5A6 #BDC3C7'
        }
    },
    {
        selector: 'node.critical',
        style: {
            'border-color': '#E74C3C',
            'border-width': 5,
            'border-style': 'double',
            'shadow-blur': 15,
            'shadow-color': 'rgba(231, 76, 60, 0.8)',
            'background-gradient-stop-colors': '#E74C3C #FF6B6B #E74C3C'
        }
    },

    // Enhanced Edge styling - Clean and professional with animations
    {
        selector: 'edge',
        style: {
            'width': 3,
            'line-color': '#BDC3C7',
            'target-arrow-color': '#BDC3C7',
            'target-arrow-shape': 'triangle',
            'target-arrow-fill': 'filled',
            'curve-style': 'bezier',
            'font-size': '9px',
            'font-family': '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
            'font-weight': '500',
            'color': '#34495E',
            'text-background-opacity': 1,
            'text-background-color': '#FFFFFF',
            'text-background-padding': '3px',
            'text-border-color': '#BDC3C7',
            'text-border-width': 1,
            'text-border-opacity': 0.7,
            'text-valign': 'center',
            'text-halign': 'center',
            'transition-property': 'width, line-color, target-arrow-color',
            'transition-duration': '0.3s'
        }
    },

    // Enhanced Edge type specific styling with distinct colors and patterns
    {
        selector: 'edge.supplies',
        style: {
            'line-color': '#27AE60',
            'target-arrow-color': '#27AE60',
            'line-style': 'solid',
            'width': 4
        }
    },
    {
        selector: 'edge.manufactures',
        style: {
            'line-color': '#3498DB',
            'target-arrow-color': '#3498DB',
            'line-style': 'solid',
            'width': 4
        }
    },
    {
        selector: 'edge.distributes',
        style: {
            'line-color': '#F39C12',
            'target-arrow-color': '#F39C12',
            'line-style': 'dashed',
            'line-dash-pattern': [6, 3],
            'width': 4
        }
    },
    {
        selector: 'edge.sells',
        style: {
            'line-color': '#9B59B6',
            'target-arrow-color': '#9B59B6',
            'line-style': 'solid',
            'width': 4
        }
    },
    {
        selector: 'edge.critical',
        style: {
            'width': 6,
            'line-color': '#E74C3C',
            'target-arrow-color': '#E74C3C',
            'line-style': 'solid',
            'shadow-blur': 8,
            'shadow-color': 'rgba(231, 76, 60, 0.5)'
        }
    },

    // Enhanced Hover effects with smooth transitions
    {
        selector: 'node:hover',
        style: {
            'border-width': 4,
            'border-color': '#2C3E50',
            'shadow-blur': 16,
            'shadow-color': 'rgba(44, 62, 80, 0.4)',
            'width': 75,
            'height': 75,
            'font-size': '12px'
        }
    },
    {
        selector: 'edge:hover',
        style: {
            'width': 5,
            'line-color': '#2C3E50',
            'target-arrow-color': '#2C3E50',
            'shadow-blur': 6,
            'shadow-color': 'rgba(44, 62, 80, 0.3)'
        }
    },

    // Enhanced Selection effects
    {
        selector: 'node:selected',
        style: {
            'border-width': 5,
            'border-color': '#2C3E50',
            'border-style': 'double',
            'shadow-blur': 20,
            'shadow-color': 'rgba(44, 62, 80, 0.8)',
            'width': 80,
            'height': 80,
            'font-size': '13px',
            'font-weight': '700'
        }
    },
    {
        selector: 'edge:selected',
        style: {
            'width': 6,
            'line-color': '#2C3E50',
            'target-arrow-color': '#2C3E50',
            'shadow-blur': 10,
            'shadow-color': 'rgba(44, 62, 80, 0.6)'
        }
    },

    // Connected edges highlighting when node is selected
    {
        selector: 'edge.connected',
        style: {
            'width': 5,
            'line-color': '#F39C12',
            'target-arrow-color': '#F39C12',
            'shadow-blur': 8,
            'shadow-color': 'rgba(243, 156, 18, 0.5)',
            'z-index': 10
        }
    },

    // Neighbor highlighting
    {
        selector: 'node.neighbor',
        style: {
            'border-width': 3,
            'border-color': '#F39C12',
            'shadow-blur': 10,
            'shadow-color': 'rgba(243, 156, 18, 0.4)'
        }
    },

    // Dimmed background elements
    {
        selector: 'node.dimmed',
        style: {
            'opacity': 0.3
        }
    },
    {
        selector: 'edge.dimmed',
        style: {
            'opacity': 0.2
        }
    }
];

const GraphVisualization = ({ graphData, onNodeSelect, loading }) => {
    const cyRef = useRef(null);
    const containerRef = useRef(null);
    const tooltipRef = useRef(null);
    const [isInitialized, setIsInitialized] = useState(false);
    const [currentTooltip, setCurrentTooltip] = useState(null);
    const [showLegend, setShowLegend] = useState(true);
    const [selectedElement, setSelectedElement] = useState(null);

    // Enhanced tooltip creation function
    const createTooltip = (element, event) => {
        const data = element.data();
        const isNode = element.isNode();
        const position = event.position || event.cyPosition;

        let tooltipContent = '';

        if (isNode) {
            // Enhanced node tooltip with downward positioning
            const properties = data.properties || {};
            const neo4jLabels = data.neo4j_labels || [];
            const nodeType = data.nodeType || 'unknown';

            tooltipContent = `
                <div style="
                    background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    max-width: 280px;
                    border: 2px solid #3498DB;
                ">
                    <div style="font-weight: 700; font-size: 15px; margin-bottom: 8px; color: #3498DB;">
                        ${data.label}
                    </div>
                    <div style="margin-bottom: 6px;">
                        <strong>Type:</strong> ${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)}
                    </div>
                    ${neo4jLabels.length > 0 ? `<div style="margin-bottom: 6px;"><strong>Labels:</strong> ${neo4jLabels.join(', ')}</div>` : ''}
                    ${Object.keys(properties).length > 0 ? `
                        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                            <div style="font-weight: 600; margin-bottom: 4px;">Properties:</div>
                            ${Object.entries(properties).slice(0, 5).map(([key, value]) =>
                                `<div style="margin-bottom: 2px; font-size: 12px;">
                                    <span style="color: #BDC3C7;">${key}:</span> ${String(value).length > 30 ? String(value).substring(0, 30) + '...' : value}
                                </div>`
                            ).join('')}
                            ${Object.keys(properties).length > 5 ? `<div style="font-size: 11px; color: #95A5A6;">...and ${Object.keys(properties).length - 5} more</div>` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            // Enhanced edge tooltip
            const properties = data.properties || {};
            const edgeType = data.edgeType || 'relationship';

            tooltipContent = `
                <div style="
                    background: linear-gradient(135deg, #34495E 0%, #2C3E50 100%);
                    color: white;
                    padding: 10px 14px;
                    border-radius: 6px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    max-width: 250px;
                    border: 2px solid #F39C12;
                ">
                    <div style="font-weight: 700; font-size: 14px; margin-bottom: 6px; color: #F39C12;">
                        ${data.label}
                    </div>
                    <div style="margin-bottom: 4px;">
                        <strong>Type:</strong> ${edgeType.charAt(0).toUpperCase() + edgeType.slice(1)}
                    </div>
                    ${Object.keys(properties).length > 0 ? `
                        <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2);">
                            ${Object.entries(properties).slice(0, 3).map(([key, value]) =>
                                `<div style="margin-bottom: 2px; font-size: 11px;">
                                    <span style="color: #BDC3C7;">${key}:</span> ${String(value).length > 25 ? String(value).substring(0, 25) + '...' : value}
                                </div>`
                            ).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }

        // Position tooltip below the element (downward positioning as requested)
        const tooltipElement = document.createElement('div');
        tooltipElement.innerHTML = tooltipContent;
        tooltipElement.style.position = 'absolute';
        tooltipElement.style.pointerEvents = 'none';
        tooltipElement.style.zIndex = '9999';

        // Calculate position - place below the element
        const containerRect = containerRef.current.getBoundingClientRect();
        const elementPosition = element.renderedPosition();
        const tooltipRect = tooltipElement.getBoundingClientRect();

        // Position below the element with some offset
        let left = containerRect.left + elementPosition.x - tooltipElement.offsetWidth / 2;
        let top = containerRect.top + elementPosition.y + (isNode ? 40 : 20); // Offset below element

        // Ensure tooltip stays within viewport
        if (left < 10) left = 10;
        if (left + tooltipElement.offsetWidth > window.innerWidth - 10) {
            left = window.innerWidth - tooltipElement.offsetWidth - 10;
        }
        if (top + tooltipElement.offsetHeight > window.innerHeight - 10) {
            // If it doesn't fit below, place it above
            top = containerRect.top + elementPosition.y - tooltipElement.offsetHeight - 10;
        }

        tooltipElement.style.left = `${left}px`;
        tooltipElement.style.top = `${top}px`;

        document.body.appendChild(tooltipElement);
        return tooltipElement;
    };

    // Enhanced relationship highlighting function
    const highlightRelationships = (element) => {
        if (!cyRef.current) return;

        const cy = cyRef.current;

        // Reset all elements
        cy.elements().removeClass('connected neighbor dimmed');

        if (element) {
            // Add connected class to directly connected edges
            element.connectedEdges().addClass('connected');

            // Add neighbor class to connected nodes
            element.neighborhood('node').addClass('neighbor');

            // Dim all other elements
            cy.elements().not(element).not(element.connectedEdges()).not(element.neighborhood()).addClass('dimmed');
        }
    };

    // Keyboard shortcuts handler
    const handleKeyPress = (event) => {
        if (!cyRef.current) return;

        const cy = cyRef.current;

        switch (event.key.toLowerCase()) {
            case 'f':
                // Fit to screen
                cy.fit();
                event.preventDefault();
                break;
            case 'c':
                // Center selected element or all elements
                if (selectedElement) {
                    cy.center(selectedElement);
                } else {
                    cy.center();
                }
                event.preventDefault();
                break;
            case 'l':
                // Toggle legend
                setShowLegend(!showLegend);
                event.preventDefault();
                break;
            case 'r':
                // Reset view
                cy.fit();
                cy.zoom(1);
                cy.center();
                event.preventDefault();
                break;
            case 'escape':
                // Clear selection and highlighting
                cy.elements().unselect();
                highlightRelationships(null);
                setSelectedElement(null);
                event.preventDefault();
                break;
        }
    };

    // Initialize Cytoscape instance
    useEffect(() => {
        if (!containerRef.current || !window.cytoscape || isInitialized) return;

        console.log('[GraphVisualization] Initializing Cytoscape...');

        const cy = window.cytoscape({
            container: containerRef.current,
            elements: [],
            style: cytoscapeStylesheet,
            layout: {
                name: 'cose',
                animate: true,
                animationDuration: 1000,
                fit: true,
                padding: 50,
                nodeRepulsion: 400000,
                nodeOverlap: 10,
                idealEdgeLength: 100,
                edgeElasticity: 100,
                nestingFactor: 5
            },
            minZoom: 0.1,
            maxZoom: 3,
            wheelSensitivity: 0.2
        });

        // Enhanced event handlers with tooltips and highlighting
        let currentTooltipElement = null;

        cy.on('mouseover', 'node, edge', (event) => {
            const element = event.target;

            // Remove existing tooltip
            if (currentTooltipElement) {
                document.body.removeChild(currentTooltipElement);
                currentTooltipElement = null;
            }

            // Create new tooltip
            currentTooltipElement = createTooltip(element, event);

            // Highlight relationships
            highlightRelationships(element);
        });

        cy.on('mouseout', 'node, edge', (event) => {
            // Remove tooltip
            if (currentTooltipElement) {
                document.body.removeChild(currentTooltipElement);
                currentTooltipElement = null;
            }

            // Reset highlighting
            highlightRelationships(null);
        });

        cy.on('tap', 'node, edge', (event) => {
            const element = event.target;
            setSelectedElement(element);

            if (element.isNode()) {
                const nodeData = element.data();
                console.log('[GraphVisualization] Node clicked:', nodeData);
                if (onNodeSelect) {
                    onNodeSelect(nodeData);
                }
            }
        });

        cy.on('tap', (event) => {
            // Click on background clears selection
            if (event.target === cy) {
                cy.elements().unselect();
                highlightRelationships(null);
                setSelectedElement(null);
            }
        });

        cyRef.current = cy;
        setIsInitialized(true);

        // Add keyboard event listener
        document.addEventListener('keydown', handleKeyPress);

        // Cleanup on unmount
        return () => {
            document.removeEventListener('keydown', handleKeyPress);
            if (cyRef.current) {
                cyRef.current.destroy();
                cyRef.current = null;
                setIsInitialized(false);
            }
        };
    }, [containerRef.current, isInitialized, onNodeSelect, createTooltip, highlightRelationships, handleKeyPress]);

    // Update graph data when it changes
    useEffect(() => {
        if (!cyRef.current || !graphData || !isInitialized) return;

        console.log('[GraphVisualization] Updating graph data...', graphData);
        
        try {
            const elements = transformDataForCytoscape(graphData);
            
            // Clear existing elements and add new ones
            cyRef.current.elements().remove();
            cyRef.current.add(elements);
            
            // Run layout
            cyRef.current.layout({ 
                name: 'cose', 
                animate: true,
                animationDuration: 1000,
                fit: true,
                padding: 50
            }).run();
            
            console.log('[GraphVisualization] Graph updated successfully');
        } catch (error) {
            console.error('[GraphVisualization] Error updating graph:', error);
        }
    }, [graphData, isInitialized]);

    return (
        <div style={{
            width: '100%',
            height: '100%',
            position: 'relative',
            background: '#FFFFFF',
            border: '1px solid #BDC3C7',
            borderRadius: '8px',
            display: 'flex',
            flexDirection: 'column'
        }}>
            {/* Legend */}
            {showLegend && (
                <div style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    background: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #BDC3C7',
                    borderRadius: '6px',
                    padding: '8px',
                    fontSize: '11px',
                    fontFamily: '"Segoe UI", Arial, sans-serif',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    zIndex: 100,
                    maxWidth: '200px'
                }}>
                    <div style={{ fontWeight: '600', marginBottom: '6px', color: '#2C3E50' }}>Node Types</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                            <div style={{ width: '12px', height: '12px', background: '#27AE60', borderRadius: '50%', border: '1px solid #229954' }}></div>
                            <span>Supplier</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                            <div style={{ width: '12px', height: '12px', background: '#3498DB', borderRadius: '4px', border: '1px solid #2980B9' }}></div>
                            <span>Manufacturer</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                            <div style={{ width: '12px', height: '12px', background: '#E74C3C', transform: 'rotate(45deg)', border: '1px solid #C0392B' }}></div>
                            <span>Customer</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                            <div style={{ width: '12px', height: '12px', background: '#F39C12', clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)', border: '1px solid #E67E22' }}></div>
                            <span>Distributor</span>
                        </div>
                    </div>
                    <div style={{ fontWeight: '600', marginTop: '8px', marginBottom: '4px', color: '#2C3E50', fontSize: '10px' }}>Hover for details</div>
                    <div style={{ fontWeight: '600', marginTop: '6px', marginBottom: '4px', color: '#2C3E50', fontSize: '10px' }}>Keyboard Shortcuts:</div>
                    <div style={{ fontSize: '9px', color: '#7F8C8D', lineHeight: '1.3' }}>
                        <div>F: Fit to screen</div>
                        <div>C: Center view</div>
                        <div>L: Toggle legend</div>
                        <div>R: Reset view</div>
                        <div>Esc: Clear selection</div>
                    </div>
                </div>
            )}

            {loading && (
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10,
                    background: 'rgba(255, 255, 255, 0.9)',
                    padding: '20px',
                    borderRadius: '8px',
                    textAlign: 'center',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                }}>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#2C3E50', marginBottom: '8px' }}>Loading graph data...</div>
                    <div style={{ fontSize: '14px', color: '#7F8C8D' }}>Building knowledge graph visualization</div>
                </div>
            )}

            {!loading && (!graphData || (!graphData.nodes || graphData.nodes.length === 0) && (!graphData.edges || graphData.edges.length === 0)) && (
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10,
                    background: 'rgba(255, 255, 255, 0.95)',
                    padding: '30px',
                    borderRadius: '12px',
                    textAlign: 'center',
                    boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
                    maxWidth: '400px',
                    border: '2px solid #BDC3C7'
                }}>
                    <div style={{
                        fontSize: '48px',
                        marginBottom: '16px',
                        color: '#BDC3C7'
                    }}>
                        📊
                    </div>
                    <div style={{
                        fontSize: '18px',
                        fontWeight: '600',
                        color: '#2C3E50',
                        marginBottom: '12px'
                    }}>
                        No Graph Data Available
                    </div>
                    <div style={{
                        fontSize: '14px',
                        color: '#7F8C8D',
                        marginBottom: '20px',
                        lineHeight: '1.5'
                    }}>
                        The knowledge graph is currently empty. Start building your graph by:
                    </div>
                    <div style={{
                        textAlign: 'left',
                        fontSize: '13px',
                        color: '#34495E',
                        marginBottom: '20px'
                    }}>
                        <div style={{ marginBottom: '8px' }}>
                            • <strong>Upload documents</strong> to extract entities and relationships
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                            • <strong>Use the chat interface</strong> to create nodes and connections
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                            • <strong>Import data</strong> from CSV or other sources
                        </div>
                        <div>
                            • <strong>Connect to data sources</strong> like databases or APIs
                        </div>
                    </div>
                    <button
                        onClick={() => window.location.reload()}
                        style={{
                            padding: '10px 20px',
                            background: '#3498DB',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '600',
                            marginRight: '10px'
                        }}
                    >
                        Refresh Data
                    </button>
                    <button
                        onClick={() => {
                            // Focus on the chat input if it exists
                            const chatInput = document.querySelector('input[type="text"], textarea');
                            if (chatInput) {
                                chatInput.focus();
                            }
                        }}
                        style={{
                            padding: '10px 20px',
                            background: '#27AE60',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '600'
                        }}
                    >
                        Start Chatting
                    </button>
                </div>
            )}
            <div
                ref={containerRef}
                style={{
                    width: '100%',
                    height: '100%',
                    borderRadius: '8px'
                }}
            />
        </div>
    );
};

export default GraphVisualization;