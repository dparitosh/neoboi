import React from 'react';

const ErrorDisplay = ({ message }) => {
    return (
        <div>
            <p style={{ color: 'red' }}>Error: {message}</p>
        </div>
    );
};

export default ErrorDisplay;
