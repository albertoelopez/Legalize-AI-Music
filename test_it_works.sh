#!/bin/bash

echo "════════════════════════════════════════════════════════"
echo "   TESTING LEGALIZE AI MUSIC APP"
echo "════════════════════════════════════════════════════════"
echo ""

cd /mnt/d/AI_Projects/ralph_app/src

echo "TEST 1: Checking if Ollama is running..."
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "✗ Ollama is NOT running - please start it with: ollama serve"
    exit 1
fi
echo ""

echo "TEST 2: Testing Ollama connection via CLI..."
../venv/bin/python -m workflow.cli test-ollama --model llama3.1:8b 2>&1 | grep -E "(Testing|✓|Connection successful)"
echo ""

echo "TEST 3: Checking status..."
../venv/bin/python -m workflow.cli status 2>&1 | grep -A 5 "Workflow Status"
echo ""

echo "TEST 4: Running simple AI task..."
echo "Prompt: 'What is MIDI in one sentence?'"
../venv/bin/python -m workflow.cli start --prompt "What is MIDI in one sentence?" --model llama3.1:8b 2>&1 | grep -E "(Starting Workflow|✓ Workflow|Agent Output:)" | head -5
echo ""

echo "════════════════════════════════════════════════════════"
echo "   TESTING COMPLETE"
echo "════════════════════════════════════════════════════════"
