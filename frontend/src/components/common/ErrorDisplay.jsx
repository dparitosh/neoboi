import React from 'react';

const ErrorDisplay = ({ message }) => {
  return (
    <div className="p-4 bg-red-100 border border-red-400 text-red-700">
      <p>{message}</p>
    </div>
  );
};

export default ErrorDisplay;
