import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

sb_admin = create_client(SUPABASE_URL, SERVICE_KEY)

def verify_access_token(access_token: str):
    """
    Validates token against Supabase. Returns user dict or None.
    """
    if not access_token:
        return None
    try:
        res = sb_admin.auth.get_user(access_token)
        return res.user
    except Exception:
        return None

def get_profile(user_id: str):
    return sb_admin.table("profiles").select("*").eq("user_id", user_id).single().execute().data