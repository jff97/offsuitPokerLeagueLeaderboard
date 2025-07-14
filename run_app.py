#!/usr/bin/env python3
"""
Entry point for running the poker scraper application.
"""

import os
from poker_scraper import app as poker_app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Default to production mode, enable debug only for local development
    debug = os.environ.get('FLASK_ENV') == 'development'
    poker_app.app.run(host='0.0.0.0', port=port, debug=debug)