import os

# Image URL Configuration
# This file contains the base URL for serving images
# Update this if your server URL changes

BASE_URL = os.getenv("IMAGE_BASE_URL", "http://localhost:8000")
IMAGE_PATH = "/static/images"
IMAGE_BASE_URL = BASE_URL.rstrip("/") + IMAGE_PATH
