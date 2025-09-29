import React, { useState, useEffect, Suspense, lazy } from 'react'
import axios from 'axios'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ErrorBoundary } from 'react-error-boundary'
import { cn } from './lib/utils'

// Lazy load components for better performance
const MainLayout = lazy(() => import('./components/layout/MainLayout'))
const GraphContainer = lazy(() => import('./components/graph/GraphContainer.jsx'))
const UnstructuredDataPage = lazy(() => import('./pages/UnstructuredDataPage'))
const LoadingSpinner = lazy(() => import('./components/common/LoadingSpinner.jsx'))
const ErrorDisplay = lazy(() => import('./components/common/ErrorDisplay.jsx'))

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex min-h-screen items-center justify-center bg-gray-100">
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-gray-600">Loading NeoBoi...</p>
    </div>
  </div>
);

// Error fallback component
const ErrorFallback = ({ error, resetErrorBoundary }) => (
  <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
    <div className="w-full max-w-md bg-white shadow-lg rounded-lg p-6">
      <h2 className="text-xl font-bold text-red-600 mb-2">Something went wrong</h2>
      <p className="text-gray-600 mb-4">
        We encountered an error while loading the application.
      </p>
      <details className="mb-4">
        <summary className="cursor-pointer text-sm font-medium text-gray-700">
          Error details
        </summary>
        <pre className="mt-2 whitespace-pre-wrap rounded-md bg-gray-100 p-3 text-xs text-gray-800">
          {error.message}
        </pre>
      </details>
      <button
        onClick={resetErrorBoundary}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Try again
      </button>
    </div>
  </div>
);

// Main App component
function App() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        setLoading(true)
        const response = await axios.get('/api/graph')
        setGraphData(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch graph data. Please ensure the backend is running.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchGraphData()
  }, [])

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <Router>
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<GraphContainer graphData={graphData} loading={loading} error={error} />} />
              <Route path="unstructured" element={<UnstructuredDataPage />} />
            </Route>
          </Routes>
        </Suspense>
      </Router>
    </ErrorBoundary>
  )
}

export default App