"""
OAuth2 authorization router.

Implements the OAuth2 authorization endpoints:
- GET /oauth/authorize - Authorization request (shows consent page)
- POST /oauth/authorize - Authorization grant (user consents)
- POST /oauth/token - Token endpoint (exchange code for tokens)
- POST /oauth/revoke - Token revocation endpoint
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from gateway.context.oauth_context import OAuthClientContext, get_oauth_client_context
from gateway.db import get_db
from gateway.db.context import set_db
from gateway.oauth2.asgi_request import ASGIOAuthRequest
#from gateway.oauth2.server import authorization_server
#from gateway.oauth2.storage import query_client

router = APIRouter(prefix="/oauth", tags=["oauth2"])

# Templates for authorization page
# Templates directory should be at src/gateway/templates
import os
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/authorize")
async def authorize_get(
    request: Request,
    db: Session = Depends(get_db),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    response_type: str = Query(...),
    scope: str = Query(default=""),
    state: str = Query(default=""),
    code_challenge: str | None = Query(default=None),
    code_challenge_method: str | None = Query(default=None),
    client_ctx: OAuthClientContext = Depends(get_oauth_client_context),
):
    set_db(db)

    return templates.TemplateResponse(
        "authorize.html",
        {
            "request": request,
            "scope": scope,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": response_type,
            "state": state,
            "code_challenge": code_challenge or "",
            "code_challenge_method": code_challenge_method or "",
            "partner_id": client_ctx.partner_id,
            "api_profile": client_ctx.api_profile,
        }
    )


@router.post("/authorize")
async def authorize_post(
    request: Request,
    db: Session = Depends(get_db),
    confirm: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    response_type: str = Form(...),
    scope: str = Form(default=""),
    state: str = Form(default=""),
    code_challenge: str = Form(default=""),
    code_challenge_method: str = Form(default=""),
    fbbid: int = Form(...),  # User identifier, passed from auth system
):
    """
    Handle POST request to authorization endpoint.
    
    Processes the user's consent and creates an authorization code.
    """
    set_db(db)
    
    if confirm != "yes":
        # User denied authorization
        error_uri = f"{redirect_uri}?error=access_denied&error_description=User+denied+authorization"
        if state:
            error_uri += f"&state={state}"
        return RedirectResponse(url=error_uri, status_code=status.HTTP_302_FOUND)
    
    # Build OAuth request from form data
    oauth_request = await ASGIOAuthRequest.from_starlette(request)
    
    # Create authorization response
    #try:
    #    response = authorization_server.create_authorization_response(
     #       request=oauth_request,
      #      grant_user=fbbid,
       # )
        
        # Extract redirect URL from response
        #if hasattr(response, "location"):
         #   return RedirectResponse(
          #      url=response.location,
           #     status_code=status.HTTP_302_FOUND
            #)
        
        # Fallback: return JSON response
        #return JSONResponse(content=response)
        
    #except Exception as e:
     #   raise HTTPException(
      #      status_code=status.HTTP_400_BAD_REQUEST,
       #     detail=str(e)
       # )


@router.post("/token")
async def token_endpoint(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    OAuth2 token endpoint.
    
    Exchanges authorization codes for access tokens,
    or refreshes access tokens using refresh tokens.
    """
    set_db(db)
    
    oauth_request = await ASGIOAuthRequest.from_starlette(request)
    
   # try:
        #response = authorization_server.create_token_response(request=oauth_request)
        
        # Authlib returns a tuple (status, headers, body) or similar
       # if isinstance(response, tuple):
        #    status_code, headers, body = response
         #   return JSONResponse(
           #     content=body if isinstance(body, dict) else {},
          #     status_code=status_code,
           #     headers=dict(headers) if headers else None
            #)
        
        #return JSONResponse(content=response)
        
   # except Exception as e:
    #    raise HTTPException(
     #       status_code=status.HTTP_400_BAD_REQUEST,
      #      detail=str(e)
       # )


@router.post("/revoke")
async def revoke_endpoint(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    OAuth2 token revocation endpoint (RFC 7009).
    
    Revokes access tokens or refresh tokens.
    """
    set_db(db)
    
    oauth_request = await ASGIOAuthRequest.from_starlette(request)
    
    try:
        # response = authorization_server.create_endpoint_response(
          #  name="revocation",
           # request=oauth_request
        #)
        
        #if isinstance(response, tuple):
         #   status_code, headers, body = response
          #  return JSONResponse(
           #     content=body if isinstance(body, dict) else {},
            #    status_code=status_code,
             #   headers=dict(headers) if headers else None
            #)
        
        # Successful revocation returns 200 with empty body
        return JSONResponse(content={}, status_code=status.HTTP_200_OK)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/introspect")
async def introspect_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Query(...),
):
    """
    OAuth2 token introspection endpoint (RFC 7662).
    
    Returns metadata about a token.
    """
    set_db(db)
    
    # For now, return a basic implementation
    # In production, this would validate the token and return its metadata
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token introspection not yet implemented"
    )
