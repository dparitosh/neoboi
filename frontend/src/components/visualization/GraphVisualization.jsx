import React, { useRef, useEffect, useState, useCallback } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import popper from 'cytoscape-popper';
import tippy from 'tippy.js';
import 'tippy.js/dist/tippy.css';

// Register Cytoscape extensions
cytoscape.use(coseBilkent);
cytoscape.use(popper);

// --- Helper Functions ---

/**
 * Transforms raw graph data from the API into the format required by Cytoscape.js.
 * It classifies nodes and edges to apply specific styles.
 * @param {object} graphData - The raw graph data from the backend.
 * @returns {Array} - An array of elements formatted for Cytoscape.
 */
function transformDataForCytoscape(graphData) {
    const elements = [];
    if (!graphData) return elements;

    // 1. Process Nodes
    if (graphData.nodes) {
        graphData.nodes.forEach(node => {
            const properties = node.properties || {};
            const name = node.label || properties.name || `Node ${node.id}`;
            const neo4jLabels = node.group ? [node.group] : (properties.labels || ['Unknown']);

            // Enhanced node type classification
            let nodeType = 'unknown';
            const typeKeywords = {
                supplier: ['supplier', 'vendor'],
                manufacturer: ['manufacturer', 'factory', 'producer'],
                customer: ['customer', 'client', 'buyer'],
                distributor: ['distributor', 'dealer'],
                retailer: ['retailer'],
                warehouse: ['warehouse', 'storage'],
                logistics: ['logistics', 'shipping'],
            };

            const checkKeywords = (text, keywords) => keywords.some(kw => text.includes(kw));

            for (const [type, keywords] of Object.entries(typeKeywords)) {
                if (checkKeywords(neo4jLabels.join(' ').toLowerCase(), keywords) || checkKeywords(name.toLowerCase(), keywords)) {
                    nodeType = type;
                    break;
                }
            }

            // Status classification for styling
            const status = (properties.status || '').toLowerCase();
            let statusClass = '';
            if (status.includes('active') || status.includes('online')) statusClass = 'active';
            else if (status.includes('inactive') || status.includes('offline')) statusClass = 'inactive';
            else if (status.includes('critical') || status.includes('error')) statusClass = 'critical';

            elements.push({
                group: 'nodes',
                data: {
                    id: String(node.id),
                    label: name,
                    neo4j_labels: neo4jLabels,
                    group: node.group || nodeType,
                    properties: properties,
                    nodeType: nodeType,
                },
                classes: `${nodeType} ${statusClass}`.trim(),
            });
        });
    }

    // 2. Process Edges
    if (graphData.edges) {
        graphData.edges.forEach(edge => {
            const properties = edge.properties || {};
            const label = edge.label || properties.type || 'RELATED_TO';

            // Edge type classification
            let edgeType = 'related';
            const labelLower = label.toLowerCase();
            if (labelLower.includes('supplies')) edgeType = 'supplies';
            else if (labelLower.includes('manufactures')) edgeType = 'manufactures';
            else if (labelLower.includes('distributes')) edgeType = 'distributes';
            else if (labelLower.includes('sells')) edgeType = 'sells';

            const isCritical = properties.status === 'CRITICAL' || properties.priority === 'HIGH';

            elements.push({
                group: 'edges',
                data: {
                    id: String(edge.id),
                    source: String(edge.from || edge.source),
                    target: String(edge.to || edge.target),
                    label: label,
                    properties: properties,
                    edgeType: edgeType,
                },
                classes: `${edgeType} ${isCritical ? 'critical' : ''}`.trim(),
            });
        });
    }

    console.log(`[Transform] Converted ${elements.length} elements for Cytoscape.`);
    return elements;
}


// --- Stylesheet ---

const cytoscapeStylesheet = [
    // Base node styling
    {
        selector: 'node',
        style: {
            'background-color': '#95A5A6', 'border-color': '#7F8C8D', 'border-width': 2,
            'label': 'data(label)', 'width': 65, 'height': 65, 'font-size': '11px',
            'font-family': '"Segoe UI", "Helvetica Neue", Arial, sans-serif', 'font-weight': '600',
            'text-valign': 'center', 'color': '#2C3E50', 'text-wrap': 'wrap', 'text-max-width': '55px',
            'transition-property': 'border-width, background-color', 'transition-duration': '0.2s'
        }
    },
    // Node type styles
    { selector: 'node.supplier', style: { 'background-color': '#27AE60', 'border-color': '#229954', 'shape': 'ellipse' } },
    { selector: 'node.manufacturer', style: { 'background-color': '#3498DB', 'border-color': '#2980B9', 'shape': 'round-rectangle' } },
    { selector: 'node.customer', style: { 'background-color': '#E74C3C', 'border-color': '#C0392B', 'shape': 'diamond' } },
    { selector: 'node.distributor', style: { 'background-color': '#F39C12', 'border-color': '#E67E22', 'shape': 'hexagon' } },
    { selector: 'node.retailer', style: { 'background-color': '#9B59B6', 'border-color': '#8E44AD', 'shape': 'star' } },
    { selector: 'node.warehouse', style: { 'background-color': '#16A085', 'border-color': '#138D75', 'shape': 'round-triangle' } },
    { selector: 'node.logistics', style: { 'background-color': '#D35400', 'border-color': '#BA4A00', 'shape': 'vee' } },
    // Status styles
    { selector: 'node.active', style: { 'border-width': 4, 'border-color': '#2ECC71' } },
    { selector: 'node.inactive', style: { 'opacity': 0.7, 'border-style': 'dashed' } },
    { selector: 'node.critical', style: { 'border-color': '#E74C3C', 'border-width': 5, 'border-style': 'double' } },
    // Base edge styling
    {
        selector: 'edge',
        style: {
            'width': 3, 'line-color': '#BDC3C7', 'target-arrow-color': '#BDC3C7', 'target-arrow-shape': 'triangle',
            'curve-style': 'bezier', 'font-size': '9px', 'font-family': '"Segoe UI", Arial, sans-serif',
            'color': '#34495E', 'text-background-opacity': 1, 'text-background-color': '#FFFFFF',
            'text-background-padding': '3px', 'text-border-color': '#BDC3C7', 'text-border-width': 1,
            'transition-property': 'width, line-color, target-arrow-color', 'transition-duration': '0.3s'
        }
    },
    // Edge type styles
    { selector: 'edge.supplies', style: { 'line-color': '#27AE60', 'target-arrow-color': '#27AE60', 'width': 4 } },
    { selector: 'edge.manufactures', style: { 'line-color': '#3498DB', 'target-arrow-color': '#3498DB', 'width': 4 } },
    { selector: 'edge.distributes', style: { 'line-color': '#F39C12', 'target-arrow-color': '#F39C12', 'line-style': 'dashed', 'width': 4 } },
    { selector: 'edge.sells', style: { 'line-color': '#9B59B6', 'target-arrow-color': '#9B59B6', 'width': 4 } },
    { selector: 'edge.critical', style: { 'width': 6, 'line-color': '#E74C3C', 'target-arrow-color': '#E74C3C' } },
    // Interaction styles
    { selector: 'node:selected', style: { 'border-width': 5, 'border-color': '#2C3E50', 'border-style': 'double' } },
    { selector: 'edge:selected', style: { 'width': 6, 'line-color': '#2C3E50', 'target-arrow-color': '#2C3E50' } },
    // Highlighting styles
    { selector: 'edge.connected', style: { 'width': 5, 'line-color': '#F39C12', 'target-arrow-color': '#F39C12', 'z-index': 10 } },
    { selector: 'node.neighbor', style: { 'border-width': 3, 'border-color': '#F39C12' } },
    { selector: '.dimmed', style: { 'opacity': 0.3 } }
];


// --- React Components ---

const Legend = () => (
    <div style={{
        position: 'absolute', top: '10px', right: '10px', background: 'rgba(255, 255, 255, 0.95)',
        border: '1px solid #BDC3C7', borderRadius: '6px', padding: '8px', fontSize: '11px',
        fontFamily: '"Segoe UI", Arial, sans-serif', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', zIndex: 100
    }}>
        <div style={{ fontWeight: '600', marginBottom: '6px', color: '#2C3E50' }}>Legend</div>
        {/* Node Types */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '12px', height: '12px', background: '#27AE60', borderRadius: '50%' }}></div>
            <span>Supplier</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '12px', height: '12px', background: '#3498DB', borderRadius: '4px' }}></div>
            <span>Manufacturer</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '12px', height: '12px', background: '#E74C3C', transform: 'rotate(45deg)' }}></div>
            <span>Customer</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '12px', height: '12px', background: '#F39C12', clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' }}></div>
            <span>Distributor</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '12px', height: '12px', background: '#9B59B6', clipPath: 'polygon(50% 0%, 93.3% 25%, 93.3% 75%, 50% 100%, 6.7% 75%, 6.7% 25%)' }}></div>
            <span>Retailer</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '12px', height: '12px', background: '#16A085', clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }}></div>
            <span>Warehouse</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '12px', height: '12px', background: '#D35400', clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' }}></div>
            <span>Logistics</span>
        </div>
        {/* Edge Types */}
        <div style={{ fontWeight: '600', marginTop: '8px', marginBottom: '4px' }}>Relationships</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '20px', height: '2px', background: '#27AE60' }}></div>
            <span>Supplies</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '20px', height: '2px', background: '#3498DB' }}></div>
            <span>Manufactures</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '20px', height: '2px', background: '#F39C12', borderStyle: 'dashed', borderWidth: '1px 0', borderColor: '#F39C12' }}></div>
            <span>Distributes</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
            <div style={{ width: '20px', height: '2px', background: '#9B59B6' }}></div>
            <span>Sells</span>
        </div>
        {/* Keyboard Shortcuts */}
        <div style={{ fontWeight: '600', marginTop: '8px', marginBottom: '4px' }}>Shortcuts</div>
        <div style={{ fontSize: '9px', color: '#7F8C8D', lineHeight: '1.3' }}>
            F: Fit, C: Center, L: Toggle Legend, R: Reset, Esc: Clear
        </div>
    </div>
);

const LoadingIndicator = () => (
    <div style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 10,
        background: 'rgba(255, 255, 255, 0.9)', padding: '20px', borderRadius: '8px', textAlign: 'center'
    }}>
        <div style={{ fontSize: '16px', fontWeight: '600', color: '#2C3E50' }}>Loading Graph...</div>
    </div>
);

const EmptyGraphMessage = () => (
    <div style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 10,
        background: 'rgba(255, 255, 255, 0.95)', padding: '30px', borderRadius: '12px', textAlign: 'center',
        border: '2px solid #BDC3C7'
    }}>
        <div style={{ fontSize: '48px', marginBottom: '16px', color: '#BDC3C7' }}>📊</div>
        <div style={{ fontSize: '18px', fontWeight: '600', color: '#2C3E50', marginBottom: '12px' }}>No Graph Data</div>
        <div style={{ fontSize: '14px', color: '#7F8C8D' }}>Upload documents or use the chat to build your knowledge graph.</div>
    </div>
);


// --- Main Component ---

const GraphVisualization = ({ graphData, onNodeSelect, loading }) => {
    const containerRef = useRef(null);
    const cyRef = useRef(null);
    const [showLegend, setShowLegend] = useState(true);

    const highlightRelationships = useCallback((element) => {
        const cy = cyRef.current;
        if (!cy) return;
        cy.elements().removeClass('connected neighbor dimmed');
        if (element && element.isNode()) {
            element.connectedEdges().addClass('connected');
            element.neighborhood('node').addClass('neighbor');
            cy.elements().not(element.neighborhood()).not(element).addClass('dimmed');
        }
    }, []);

    // Initialize Cytoscape
    useEffect(() => {
        if (!containerRef.current) return;

        const cy = cytoscape({
            container: containerRef.current,
            style: cytoscapeStylesheet,
            layout: { name: 'cose-bilkent', animate: 'end', animationDuration: 1000, fit: true, padding: 50 },
            minZoom: 0.1, maxZoom: 3,
        });
        cyRef.current = cy;

        // --- Event Handlers ---
        let tippyInstance;

        const makeTippy = (target, text) => {
            const ref = target.popperRef();
            return tippy(document.createElement('div'), {
                getReferenceClientRect: ref.getBoundingClientRect,
                content: () => {
                    const div = document.createElement('div');
                    div.innerHTML = text;
                    return div;
                },
                trigger: 'manual', allowHTML: true, arrow: true,
                placement: 'bottom', hideOnClick: false, interactive: true,
                theme: 'light-border',
            });
        };

        cy.on('mouseover', 'node, edge', (e) => {
            const el = e.target;
            const props = el.data('properties');
            let content = `<strong>${el.data('label')}</strong><hr/>`;
            for (const [key, value] of Object.entries(props)) {
                content += `<strong>${key}:</strong> ${value}<br/>`;
            }
            tippyInstance = makeTippy(el, content);
            tippyInstance.show();
            highlightRelationships(el);
        });

        cy.on('mouseout', 'node, edge', () => {
            if (tippyInstance) tippyInstance.destroy();
            highlightRelationships(null);
        });

        cy.on('tap', 'node', (e) => {
            if (onNodeSelect) onNodeSelect(e.target.data());
        });

        cy.on('tap', (e) => {
            if (e.target === cy) {
                cy.elements().unselect();
                highlightRelationships(null);
            }
        });

        // Keyboard shortcuts
        const handleKeyPress = (e) => {
            if (!cyRef.current) return;
            switch (e.key.toLowerCase()) {
                case 'f': cy.fit(null, 50); break;
                case 'c': cy.center(cy.$(':selected')); break;
                case 'l': setShowLegend(prev => !prev); break;
                case 'r': cy.layout({ name: 'cose-bilkent', animate: true }).run(); break;
                case 'escape': cy.elements().unselect(); highlightRelationships(null); break;
            }
        };
        document.addEventListener('keydown', handleKeyPress);

        return () => {
            document.removeEventListener('keydown', handleKeyPress);
            cy.destroy();
        };
    }, [onNodeSelect, highlightRelationships]);

    // Update graph data when prop changes
    useEffect(() => {
        const cy = cyRef.current;
        if (!cy || !graphData) return;

        const elements = transformDataForCytoscape(graphData);
        cy.elements().remove();
        cy.add(elements);

        const layout = cy.layout({
            name: 'cose-bilkent',
            animate: 'end',
            animationDuration: 1000,
            fit: true,
            padding: 50,
            nodeRepulsion: 4500,
            idealEdgeLength: 150,
        });
        layout.run();

    }, [graphData]);

    const isGraphEmpty = !graphData || (!graphData.nodes?.length && !graphData.edges?.length);

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative', background: '#FFFFFF', border: '1px solid #BDC3C7', borderRadius: '8px' }}>
            {showLegend && <Legend />}
            {loading && <LoadingIndicator />}
            {!loading && isGraphEmpty && <EmptyGraphMessage />}
            <div ref={containerRef} style={{ width: '100%', height: '100%', borderRadius: '8px' }} />
        </div>
    );
};

export default GraphVisualization;