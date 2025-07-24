from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create Limiter instance to be bound to a api
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2 per second", "15 per minute", "270 per hour"]
)