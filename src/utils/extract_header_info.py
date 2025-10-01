from typing import Optional

from fastapi import Request


def extract_device_info(request: Request) -> Optional[str]:
    """Extract device information from request"""
    try:
        # Prefer X-Device-Info header if present
        device_info = request.headers.get("x-device-info")
        if device_info:
            return device_info
        return None
    except Exception:
        return None


def extract_ip_address(request: Request) -> Optional[str]:
    """Extract IP address from request"""
    try:
        # Check for forwarded IP first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to client IP
        return request.client.host if request.client else None
    except Exception:
        return None
