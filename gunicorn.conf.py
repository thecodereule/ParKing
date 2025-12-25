import os

bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = 2
timeout = 120