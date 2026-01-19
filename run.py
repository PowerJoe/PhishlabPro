#!/usr/bin/env python3
"""
PhishLab Pro - AI-Powered Phishing Platform
Educational & Research Purposes Only
"""

import os
from app import create_app, socketio

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              PHISHLAB PRO v1.0.0                         ║
    ║          AI-Powered Phishing Platform                    ║
    ║                                                           ║
    ║  ⚠️  EDUCATIONAL & RESEARCH PURPOSES ONLY  ⚠️           ║
    ║                                                           ║
    ║  Unauthorized use is strictly prohibited and illegal.    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Starting server...
    📡 Access at: http://localhost:5000
    
    First time? Create super admin at: http://localhost:5000/auth/register
    """)
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
