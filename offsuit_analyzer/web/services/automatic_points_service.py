import os
from cryptography.fernet import Fernet
from offsuit_analyzer import data_service


def _get_cipher():
    """Get the Fernet cipher instance using the encryption key from environment."""
    key = os.getenv("TOKEN_ENCRYPTION_KEY")
    if not key:
        raise ValueError("TOKEN_ENCRYPTION_KEY environment variable not set")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_token(token: str) -> str:
    """Encrypt a token for public API exposure.
    
    Args:
        token: The token to encrypt
        
    Returns:
        str: The encrypted token (URL-safe base64)
    """
    cipher = _get_cipher()
    encrypted = cipher.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted token sent from the frontend.
    
    Args:
        encrypted_token: The encrypted token string
        
    Returns:
        str: The decrypted original token
        
    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    cipher = _get_cipher()
    decrypted = cipher.decrypt(encrypted_token.encode())
    return decrypted.decode()


def get_bar_list():
    """Get public bar list with encrypted token IDs.
    
    Returns:
        list: Bar list with tokens encrypted and exposed as bar_id
    """
    bars = data_service.get_bar_list_public()
    
    # Encrypt tokens in the web service layer
    for bar in bars:
        bar['bar_id'] = encrypt_token(bar.pop('token'))
    
    return bars


def get_token_from_bar_id(bar_id: str) -> str:
    """Decrypt a bar_id to get the actual token.
    
    Args:
        bar_id: The encrypted bar ID from the frontend
        
    Returns:
        str: The decrypted token
        
    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    return decrypt_token(bar_id)
