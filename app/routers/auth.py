import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.vk_account import VkAccount, PasswordResetToken
from app.schemas.user import (
    UserCreate,
    UserMe,
    LoginRequest,
    RegisterResponse,
    TokenResponse,
    RefreshRequest,
    VkAuthRequest,
    VkTokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    LinkVkRequest,
    LinkVkResponse,
)
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    rotate_refresh_token,
    get_current_user,
    exchange_vk_code,
    _hash_token,
    generate_refresh_token_string,
    process_password_reset_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
    )
    db.add(user)
    await db.flush()
    return RegisterResponse(message="ok")


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(db, user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    user_id, new_refresh = await rotate_refresh_token(db, refresh_data.refresh_token)
    access_token = create_access_token(user_id)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


@router.post("/vk", response_model=VkTokenResponse)
async def vk_auth(vk_data: VkAuthRequest, db: AsyncSession = Depends(get_db)):
    vk_info = await exchange_vk_code(vk_data.code, vk_data.redirect_uri)

    # Check if VK account already linked
    result = await db.execute(
        select(VkAccount).where(VkAccount.vk_user_id == vk_info["vk_user_id"])
    )
    existing_vk = result.scalar_one_or_none()

    if existing_vk:
        # Login existing user
        user = existing_vk.user
        is_new_user = False
    else:
        is_new_user = True
        user = None

        # Check if email from VK matches existing user (auto-link)
        if vk_info["email"]:
            result = await db.execute(
                select(User).where(User.email == vk_info["email"])
            )
            user = result.scalar_one_or_none()
            if user:
                is_new_user = False

        # Create new user if not found
        if user is None:
            name = f"{vk_info['first_name']} {vk_info['last_name']}".strip()
            if not name:
                name = f"vk_user_{vk_info['vk_user_id']}"
            user = User(
                email=vk_info.get("email"),
                name=name,
            )
            db.add(user)
            await db.flush()

        # Create VK account record
        vk_account = VkAccount(
            user_id=user.id,
            vk_user_id=vk_info["vk_user_id"],
            access_token=vk_info["vk_access_token"],
            email=vk_info.get("email"),
            profile_data=vk_info["profile_data"],
        )
        db.add(vk_account)

    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(db, user.id)
    return VkTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        is_new_user=is_new_user,
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    fp_data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == fp_data.email))
    user = result.scalar_one_or_none()

    if user:
        raw_token = generate_refresh_token_string()
        token_hash = _hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        prt = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.add(prt)
        await db.flush()

        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={raw_token}"
        logger.info(f"Password reset link for {fp_data.email}: {reset_link}")

    return ForgotPasswordResponse(message="if email exists, link sent")


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    rp_data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    user = await process_password_reset_token(db, rp_data.token)
    user.password_hash = hash_password(rp_data.new_password)
    await db.flush()
    return ResetPasswordResponse(message="password updated")


@router.post("/link-vk", response_model=LinkVkResponse)
async def link_vk(
    link_data: LinkVkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vk_info = await exchange_vk_code(link_data.code, link_data.redirect_uri)

    # Check if VK account already linked to someone
    result = await db.execute(
        select(VkAccount).where(VkAccount.vk_user_id == vk_info["vk_user_id"])
    )
    existing_vk = result.scalar_one_or_none()
    if existing_vk:
        if existing_vk.user_id == current_user.id:
            return LinkVkResponse(vk_linked=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VK account already linked to another user",
        )

    vk_account = VkAccount(
        user_id=current_user.id,
        vk_user_id=vk_info["vk_user_id"],
        access_token=vk_info["vk_access_token"],
        email=vk_info.get("email"),
        profile_data=vk_info["profile_data"],
    )
    db.add(vk_account)
    await db.flush()
    return LinkVkResponse(vk_linked=True)


@router.get("/me", response_model=UserMe)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VkAccount).where(VkAccount.user_id == current_user.id)
    )
    vk_account = result.scalar_one_or_none()
    vk_linked = vk_account is not None

    return UserMe(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        vk_linked=vk_linked,
    )