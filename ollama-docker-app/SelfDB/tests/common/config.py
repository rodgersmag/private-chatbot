"""
Static configuration for SelfDB test suite.
"""

import os
from dotenv import load_dotenv

# Load environment variables from root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../.env'))

# API endpoints
BACKEND_URL = 'http://localhost:8000/api/v1'
STORAGE_URL = 'http://localhost:8001'
API_KEY = os.getenv("ANON_KEY")

# Test credentials
TEST_EMAIL_BASE = "testuser"
TEST_PASSWORD = "password123"

# Admin credentials for cleanup operations
ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")
