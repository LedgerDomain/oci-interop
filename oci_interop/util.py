import jwt
import os
import time

def get_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        raise Exception(f'Environment variable {name} not set')

def jwt_is_expired(j: str) -> bool:
    """
    Returns True if the JWT token is expired, False otherwise.
    """
    decoded_token = jwt.decode(j, options={'verify_signature': False})
    expiration_timestamp = decoded_token['exp']
    # Get the current timestamp
    current_timestamp = int(time.time())
    # Check if the token is expired
    return current_timestamp >= expiration_timestamp
