const express = require('express');
const path = require('path');
const cors = require('cors');

// Check for development mode
const isDev = process.argv.includes('--dev');

const app = express();
const PORT = process.env.FRONTEND_PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3001';

// Middleware
app.use(cors());
app.use(express.json());

// Set MIME type for JSX files
app.use((req, res, next) => {
    if (req.url.endsWith('.jsx')) {
        res.setHeader('Content-Type', 'application/javascript');
    }
    next();
});

// Development mode: Add request logging
if (isDev) {
    app.use((req, res, next) => {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${req.method} ${req.url}`);
        next();
    });
}

// Serve static files
app.use(express.static(path.join(__dirname, 'static')));
app.use('/src', express.static(path.join(__dirname, 'src')));

// API proxy to backend
app.use('/api', (req, res) => {
    const backendUrl = `${BACKEND_URL}${req.originalUrl}`;

    // Proxy the request to backend
    const http = require('http');
    const https = require('https');
    const url = require('url');

    const parsedUrl = url.parse(backendUrl);
    const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port,
        path: parsedUrl.path,
        method: req.method,
        headers: req.headers
    };

    const proxyReq = (parsedUrl.protocol === 'https:' ? https : http).request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
        console.error('Proxy error:', err);
        res.status(500).json({ error: 'Backend service unavailable' });
    });

    // Pipe request body
    req.pipe(proxyReq);
});

// Serve the main HTML file for all non-API routes
app.get('/unstructured', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'unstructured.html'));
});

// Serve the main HTML file for all other non-API routes (excluding static files)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'frontend',
        mode: isDev ? 'development' : 'production',
        backend_url: BACKEND_URL,
        timestamp: new Date().toISOString()
    });
});

// Start server
app.listen(PORT, () => {
    const mode = isDev ? 'DEVELOPMENT' : 'PRODUCTION';
    console.log(`🚀 Frontend server (${mode}) running on http://localhost:${PORT}`);
    console.log(`🔗 Backend API: ${BACKEND_URL}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);

    if (isDev) {
        console.log(`🔄 Development mode: Request logging enabled`);
        console.log(`📝 Edit frontend files and restart server to see changes`);
    }
});

module.exports = app;