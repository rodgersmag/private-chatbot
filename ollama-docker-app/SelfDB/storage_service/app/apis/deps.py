from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Union, Literal
from pydantic import BaseModel

from ..core.config import settings

security = HTTPBearer(auto_error=False)
ANON_USER_ROLE = "anon"

class TokenData(BaseModel):
    sub: Optional[str] = None
    is_superuser: bool = False        # NEW

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Validate JWT token and return user information.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        super_flag: bool = payload.get("is_superuser", False)  # NEW
        if user_id is None:
            return None
        # Convert exp to int if it's a float to avoid validation errors
        exp_value = payload.get("exp")
        if isinstance(exp_value, float):
            exp_value = int(exp_value)
        token_data = TokenData(sub=user_id, is_superuser=super_flag)  # NEW
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data

async def get_current_user_or_anon(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Union[TokenData, Literal["anon"]]:
    """
    Get current user from JWT token or validate anonymous API key.
    Returns user data or "anon" for anonymous access.
    """
    # No credentials provided
    if not credentials:
        # Check for anon key in query params (would require additional parameter)
        # For now, just return None to indicate no authentication
        return None
    
    # Check if it's a JWT token
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id:
            # Convert exp to int if it's a float to avoid validation errors
            exp_value = payload.get("exp")
            if isinstance(exp_value, float):
                exp_value = int(exp_value)
            super_flag: bool = payload.get("is_superuser", False)
            return TokenData(sub=user_id, is_superuser=super_flag)
    except JWTError:
        pass  # Not a valid JWT, continue to check if it's an anon key
    
    # Check if it's the anonymous API key
    if credentials.credentials == settings.ANON_KEY:
        return ANON_USER_ROLE
    
    # Neither valid JWT nor anon key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
