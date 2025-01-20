#!/usr/bin/env bash
 
# Start Ollama in the background
ollama serve &
sleep 5
 
# Pull and run phi4
ollama pull vanilj/phi-4-unsloth
 
# Restart ollama and run it in to foreground.
pkill -f "ollama"
ollama serve