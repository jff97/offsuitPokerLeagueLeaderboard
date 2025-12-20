#!/bin/bash
# Startup script for Azure Web App
gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 600 offsuit_analyzer.web.app:app
