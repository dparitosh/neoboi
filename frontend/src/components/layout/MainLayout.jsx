import React from 'react';

const MainLayout = ({ children }) => {
    return (
        <div>
            <h1>Neo4j Graph Visualization</h1>
            {children}
        </div>
    );
};

export default MainLayout;
