#!/usr/bin/env python3
"""
Test CORS origins configuration
"""
import sys
import os
sys.path.append('sop-portal-backend')

from app.config.settings import settings

print("🔍 Checking CORS Configuration...")
print(f"CORS_ORIGINS string: {settings.CORS_ORIGINS}")
print(f"CORS origins list: {settings.cors_origins_list}")
print(f"Netlify URL in list: {'https://soptest.netlify.app' in settings.cors_origins_list}")
print(f"Localhost URLs in list: {[url for url in settings.cors_origins_list if 'localhost' in url]}")
