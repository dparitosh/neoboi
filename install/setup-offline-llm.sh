#!/bin/bash

echo "Setting up Offline LLM Integration for Neo4j Graph App"
echo "===================================================="

echo ""
echo "Step 1: Installing Ollama (if not already installed)"
echo "Download from: https://ollama.ai/download"
echo "After installation, run: ollama serve"

echo ""
echo "Step 2: Pulling required models"
echo "Run these commands in separate terminals:"
echo "ollama pull llama2"
echo "ollama pull codellama"

echo ""
echo "Step 3: Installing Node.js dependencies"
npm install

echo ""
echo "Step 4: Starting the application"
echo "The app will automatically initialize the offline LLM service"
npm start

echo ""
echo "Available Models:"
echo "- llama2 (default, good for general queries)"
echo "- codellama (better for technical/code-related queries)"
echo "- mistral (alternative model)"

echo ""
echo "To switch models, modify the model property in offlineLLMService.js"
echo ""