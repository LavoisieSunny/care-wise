from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.services.auth_service import auth_service
from app.core.security import get_current_user

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse, tags=["Auth"])
async def register(req: UserRegister):
    try:
        user = auth_service.register(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = auth_service.create_access_token(user.id)
    return TokenResponse(access_token=token, user=user)


@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(req: UserLogin):
    user = auth_service.authenticate(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = auth_service.create_access_token(user.id)
    return TokenResponse(access_token=token, user=user)


@router.get("/auth/me", response_model=UserOut, tags=["Auth"])
async def me(current_user: UserOut = Depends(get_current_user)):
    return current_user
