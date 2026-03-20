import os
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError


def _get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _quote_object_path(object_path: str) -> str:
    # Supabase Storage object names are embedded in URLs. Encode each path segment
    # but keep slashes as separators.
    return "/".join(urllib.parse.quote(part, safe="") for part in object_path.split("/"))


def upload_to_supabase_storage(
    *,
    file_obj,
    object_path: str,
    content_type: str,
    bucket: str | None = None,
) -> str:
    """
    Upload bytes to Supabase Storage and return the (public) object URL.

    Assumes the storage bucket is public.
    """
    supabase_url = _get_required_env("SUPABASE_URL").rstrip("/")
    service_role_key = _get_required_env("SUPABASE_SERVICE_ROLE_KEY")
    bucket = bucket or _get_required_env("SUPABASE_STORAGE_BUCKET")

    quoted_object_path = _quote_object_path(object_path)

    upload_url = f"{supabase_url}/storage/v1/object/{bucket}/{quoted_object_path}"
    public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{quoted_object_path}"

    file_bytes = file_obj.read()

    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": content_type or "application/octet-stream",
        # Overwrite existing object if it already exists at the same path.
        "x-upsert": "true",
    }

    req = urllib.request.Request(upload_url, data=file_bytes, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            # Response body is not needed for the public URL we return.
            _ = resp.read()
    except HTTPError as e:
        # Include response body when available to simplify debugging.
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = "<unavailable>"
        raise RuntimeError(f"Supabase upload failed ({e.code}): {body}") from e
    except URLError as e:
        raise RuntimeError(f"Supabase upload failed: {e.reason}") from e

    return public_url

