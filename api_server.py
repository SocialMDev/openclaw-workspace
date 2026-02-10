#!/usr/bin/env python3
"""
OpenClaw API Server
===================

HTTP API for OpenClaw AI assistant.

Endpoints:
    POST /chat - Send a message
    GET /history/<user_id> - Get conversation history
    GET /info/<user_id> - Get user info
    POST /clear/<user_id> - Clear user history

Usage:
    python api_server.py
    
Then:
    curl -X POST http://localhost:8080/chat \
         -H "Content-Type: application/json" \
         -d '{"user_id": "user1", "message": "Hello!"}'
"""

import sys
import json
import logging
from flask import Flask, request, jsonify

# Add paths
sys.path.insert(0, '/home/faisal/.openclaw/workspace')
sys.path.insert(0, '/home/faisal/.openclaw/workspace/honcho-ai/sdks/python/src')

from main import OpenClaw

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Initialize OpenClaw
openclaw = OpenClaw()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "openclaw",
        "memory": "honcho",
        "version": "1.0.0"
    })


@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint.
    
    Request:
        {
            "user_id": "string",
            "message": "string"
        }
    
    Response:
        {
            "user_id": "string",
            "message": "string",
            "response": "string"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not user_id or not message:
            return jsonify({"error": "user_id and message required"}), 400
        
        # Get response
        response = openclaw.chat(user_id, message)
        
        return jsonify({
            "user_id": user_id,
            "message": message,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """
    Get conversation history.
    
    Response:
        {
            "user_id": "string",
            "messages": [
                {"role": "user", "content": "...", "created_at": "..."}
            ]
        }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        history = openclaw.get_history(user_id, limit)
        
        return jsonify({
            "user_id": user_id,
            "messages": history
        })
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/info/<user_id>', methods=['GET'])
def get_info(user_id):
    """
    Get user info.
    
    Response:
        {
            "user_id": "string",
            "message_count": 10,
            "first_seen": "...",
            "last_active": "..."
        }
    """
    try:
        info = openclaw.get_user_info(user_id)
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"Error getting info: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/clear/<user_id>', methods=['POST'])
def clear_history(user_id):
    """
    Clear user history.
    
    Response:
        {
            "success": true,
            "user_id": "string"
        }
    """
    try:
        success = openclaw.clear_history(user_id)
        
        return jsonify({
            "success": success,
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 OpenClaw API Server")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health           - Health check")
    print("  POST /chat             - Send message")
    print("  GET  /history/<user>   - Get history")
    print("  GET  /info/<user>      - Get user info")
    print("  POST /clear/<user>     - Clear history")
    print("\nRunning on http://localhost:8080")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=False)
