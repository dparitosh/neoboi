@echo off
echo Setting up Python LLM Environment for Neo4j Graph App
echo ====================================================

echo.
echo Step 1: Installing Python dependencies
echo Make sure you have Python 3.8+ installed
echo.

pip install -r requirements.txt

echo.
echo Step 2: Downloading the LLM model
echo This may take several minutes depending on your internet connection
echo.

python -c "
import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
from transformers import AutoTokenizer, AutoModelForCausalLM
print('Downloading microsoft/DialoGPT-medium model...')
tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium')
model = AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-medium')
print('Model downloaded successfully!')
"

echo.
echo Step 3: Testing the Python LLM service
echo.

python python_llm_service.py --test

echo.
echo Setup complete! You can now start the Python LLM service with:
echo python python_llm_service.py
echo.

pause