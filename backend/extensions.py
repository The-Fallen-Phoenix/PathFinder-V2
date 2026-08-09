from flask_caching import Cache
from flask_jwt_extended import JWTManager

# Centralized extension instances to avoid double import/__main__ mismatch issues
cache = Cache()
jwt = JWTManager()
