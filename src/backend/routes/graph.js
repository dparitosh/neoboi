import express from 'express';
import { getGraphData, executeQuery } from '../neo4jService.js';

const router = express.Router();

router.get('/graph', async (req, res) => {
  try {
    const graphData = await getGraphData();
    res.json(graphData);
  } catch (error) {
    console.error('Error fetching default graph data:', error);
    res.status(500).json({ error: 'Failed to fetch graph data', details: error.message });
  }
});

router.post('/query', async (req, res) => {
  try {
    const { query, params } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }
    const resultData = await executeQuery(query, params || {});
    res.json(resultData);
  } catch (error) {
    console.error('Error executing query:', error);
    res.status(500).json({ error: 'Failed to execute query', details: error.message, code: error.code });
  }
});

export default router;