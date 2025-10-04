import React, { useState, useMemo } from 'react';

const DataTable = ({ graphData, loading }) => {
    const [sortColumn, setSortColumn] = useState('label');
    const [sortDirection, setSortDirection] = useState('asc');
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage] = useState(10);

    // Sorting and pagination functions
    const handleSort = (column) => {
        const direction = sortColumn === column && sortDirection === 'asc' ? 'desc' : 'asc';
        setSortColumn(column);
        setSortDirection(direction);
        setCurrentPage(1); // Reset to first page when sorting
    };

    const handlePageChange = (page) => {
        setCurrentPage(page);
    };

    // Process and sort data
    const sortedData = useMemo(() => {
        if (!graphData || !graphData.nodes) return [];
        
        const data = [...graphData.nodes];
        
        data.sort((a, b) => {
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
                    aValue = String(a.id);
                    bValue = String(b.id);
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

        return data;
    }, [graphData, sortColumn, sortDirection]);

    // Get paginated data
    const getPaginatedData = () => {
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        return sortedData.slice(startIndex, endIndex);
    };

    const getTotalPages = () => {
        return Math.ceil(sortedData.length / rowsPerPage);
    };

    const getSortIcon = (column) => {
        if (sortColumn !== column) return '⇅';
        return sortDirection === 'asc' ? '↑' : '↓';
    };

    if (loading) {
        return (
            <div style={{
                padding: '20px',
                textAlign: 'center',
                color: '#7F8C8D',
                background: '#FFFFFF',
                border: '1px solid #BDC3C7',
                borderRadius: '8px'
            }}>
                Loading table data...
            </div>
        );
    }

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        return (
            <div style={{
                padding: '20px',
                textAlign: 'center',
                color: '#7F8C8D',
                background: '#FFFFFF',
                border: '1px solid #BDC3C7',
                borderRadius: '8px'
            }}>
                No data available
            </div>
        );
    }

    return (
        <div style={{
            background: '#FFFFFF',
            border: '1px solid #BDC3C7',
            borderRadius: '8px',
            height: '100%',
            display: 'flex',
            flexDirection: 'column'
        }}>
            {/* Table Header */}
            <div style={{
                padding: '16px',
                borderBottom: '1px solid #BDC3C7',
                background: '#F8F9FA',
                borderRadius: '8px 8px 0 0'
            }}>
                <h3 style={{ 
                    margin: 0, 
                    color: '#2C3E50',
                    fontSize: '16px',
                    fontWeight: '600'
                }}>
                    Graph Data Table
                </h3>
                <p style={{
                    margin: '4px 0 0 0',
                    fontSize: '12px',
                    color: '#7F8C8D'
                }}>
                    {sortedData.length} nodes • Click column headers to sort
                </p>
            </div>

            {/* Table Content */}
            <div style={{ 
                flex: 1, 
                overflowY: 'auto',
                padding: '16px'
            }}>
                <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    fontSize: '14px'
                }}>
                    <thead>
                        <tr>
                            <th
                                onClick={() => handleSort('type')}
                                style={{
                                    padding: '12px 8px',
                                    border: '1px solid #BDC3C7',
                                    background: '#F8F9FA',
                                    textAlign: 'left',
                                    cursor: 'pointer',
                                    userSelect: 'none',
                                    fontWeight: '600',
                                    color: '#2C3E50',
                                    borderRadius: '4px 0 0 4px'
                                }}
                            >
                                Type {getSortIcon('type')}
                            </th>
                            <th
                                onClick={() => handleSort('label')}
                                style={{
                                    padding: '12px 8px',
                                    border: '1px solid #BDC3C7',
                                    background: '#F8F9FA',
                                    textAlign: 'left',
                                    cursor: 'pointer',
                                    userSelect: 'none',
                                    fontWeight: '600',
                                    color: '#2C3E50'
                                }}
                            >
                                Label {getSortIcon('label')}
                            </th>
                            <th
                                onClick={() => handleSort('id')}
                                style={{
                                    padding: '12px 8px',
                                    border: '1px solid #BDC3C7',
                                    background: '#F8F9FA',
                                    textAlign: 'left',
                                    cursor: 'pointer',
                                    userSelect: 'none',
                                    fontWeight: '600',
                                    color: '#2C3E50'
                                }}
                            >
                                ID {getSortIcon('id')}
                            </th>
                            <th
                                onClick={() => handleSort('connections')}
                                style={{
                                    padding: '12px 8px',
                                    border: '1px solid #BDC3C7',
                                    background: '#F8F9FA',
                                    textAlign: 'left',
                                    cursor: 'pointer',
                                    userSelect: 'none',
                                    fontWeight: '600',
                                    color: '#2C3E50',
                                    borderRadius: '0 4px 4px 0'
                                }}
                            >
                                Connections {getSortIcon('connections')}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {getPaginatedData().map((node, index) => (
                            <tr key={node.id || index} style={{
                                backgroundColor: index % 2 === 0 ? '#FFFFFF' : '#F8F9FA'
                            }}>
                                <td style={{ 
                                    padding: '12px 8px', 
                                    border: '1px solid #BDC3C7',
                                    color: '#2C3E50'
                                }}>
                                    <span style={{
                                        padding: '4px 8px',
                                        borderRadius: '12px',
                                        fontSize: '12px',
                                        fontWeight: '500',
                                        background: getTypeColor(node.group || 'Unknown'),
                                        color: '#FFFFFF'
                                    }}>
                                        {node.group || 'Unknown'}
                                    </span>
                                </td>
                                <td style={{ 
                                    padding: '12px 8px', 
                                    border: '1px solid #BDC3C7',
                                    color: '#2C3E50',
                                    fontWeight: '500'
                                }}>
                                    {node.label || 'Unnamed'}
                                </td>
                                <td style={{ 
                                    padding: '12px 8px', 
                                    border: '1px solid #BDC3C7',
                                    color: '#7F8C8D',
                                    fontFamily: 'monospace'
                                }}>
                                    {node.id}
                                </td>
                                <td style={{ 
                                    padding: '12px 8px', 
                                    border: '1px solid #BDC3C7',
                                    color: '#2C3E50',
                                    textAlign: 'center'
                                }}>
                                    <span style={{
                                        padding: '2px 8px',
                                        borderRadius: '8px',
                                        fontSize: '12px',
                                        background: '#E8F4FD',
                                        color: '#2980B9',
                                        fontWeight: '500'
                                    }}>
                                        {graphData.edges?.filter(edge => edge.from === node.id || edge.to === node.id).length || 0}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination Controls */}
            <div style={{
                padding: '16px',
                borderTop: '1px solid #BDC3C7',
                background: '#F8F9FA',
                borderRadius: '0 0 8px 8px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div style={{
                    fontSize: '14px',
                    color: '#7F8C8D'
                }}>
                    Showing {Math.min((currentPage - 1) * rowsPerPage + 1, sortedData.length)} to {Math.min(currentPage * rowsPerPage, sortedData.length)} of {sortedData.length} nodes
                </div>
                <div style={{
                    display: 'flex',
                    gap: '8px',
                    alignItems: 'center'
                }}>
                    <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        style={{
                            padding: '8px 16px',
                            background: currentPage === 1 ? '#95A5A6' : '#3498DB',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                            fontSize: '14px',
                            fontWeight: '500'
                        }}
                    >
                        Previous
                    </button>
                    <span style={{
                        fontSize: '14px',
                        color: '#2C3E50',
                        margin: '0 8px',
                        fontWeight: '500'
                    }}>
                        Page {currentPage} of {getTotalPages()}
                    </span>
                    <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === getTotalPages()}
                        style={{
                            padding: '8px 16px',
                            background: currentPage === getTotalPages() ? '#95A5A6' : '#3498DB',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: currentPage === getTotalPages() ? 'not-allowed' : 'pointer',
                            fontSize: '14px',
                            fontWeight: '500'
                        }}
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    );
};

// Helper function to get color for node types
const getTypeColor = (type) => {
    const colors = {
        'supplier': '#27AE60',
        'manufacturer': '#3498DB',
        'customer': '#E74C3C',
        'distributor': '#F39C12',
        'retailer': '#9B59B6',
        'warehouse': '#16A085',
        'logistics': '#D35400',
        'Unknown': '#95A5A6'
    };
    return colors[type] || colors['Unknown'];
};

export default DataTable;
