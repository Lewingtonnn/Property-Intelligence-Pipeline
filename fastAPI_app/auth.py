# -------------------------
# Auth dependency
# -------------------------
from typing import Annotated
import os
from fastapi import Header, HTTPException
class Authorisation:
    async def __call__(self, x_token: Annotated[str, Header()]) -> str:
        token = os.getenv("API_TOKEN")
        if x_token != token:
            raise HTTPException(status_code=403, detail="Invalid Token")
        return x_token