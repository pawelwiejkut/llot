import base64
import json
from flask import make_response, Response
from app.routes import favicon_bp


def _nocache(resp: Response) -> Response:
    """Add no-cache headers to response."""
    resp.headers["Cache-Control"] = "no-store, max-age=0, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


# Favicon data
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#60a5fa;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="16" ry="16" fill="url(#bg)"/>
  <!-- Translation arrows -->
  <path d="M16 24 L28 24 M25 21 L28 24 L25 27" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 40 L36 40 M39 37 L36 40 L39 43" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Text "lt" -->
  <text x="32" y="35" font-family="SF Pro Display, -apple-system, system-ui, sans-serif" font-size="18" font-weight="600" text-anchor="middle" fill="#ffffff">lt</text>
  <!-- Decorative dots -->
  <circle cx="20" cy="48" r="2" fill="url(#accent)" opacity="0.8"/>
  <circle cx="44" cy="16" r="2" fill="url(#accent)" opacity="0.8"/>
</svg>"""

SAFARI_PINNED_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <path d="M0 0h64v64H0z" fill="black"/>
  <!-- Translation arrows (simplified) -->
  <path d="M16 24 L28 24 M25 21 L28 24 L25 27" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 40 L36 40 M39 37 L36 40 L39 43" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Text "lt" -->
  <circle cx="26" cy="35" r="3" fill="white"/>
  <circle cx="38" cy="35" r="3" fill="white"/>
  <rect x="24" y="32" width="4" height="12" fill="white"/>
  <rect x="36" y="44" width="8" height="4" fill="white"/>
</svg>"""

# Base64 encoded favicon data
FAVICON_PNG_32_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAyUlEQVR4nGNkQAOqya//o4tRE9yeK8qIzGeip+XY7GDCJUEvRzDR23J0RzAOhOXIgImwklEHDHMHsKALmKuzMiwu5Yfzs6Z+Ythz/hdWzcf6hBhE+Ij3w6PXfxlcKt+jiA2+ECAFWBW9Q+G7GLIxTMvmg/MT+j4yHLv2G68ZAx4Cow4YdcCoA0YdQLAkRC7ZkMGKgz8Y6hZ/odgBAx4Co02yUQcMvAPQ+2r0BLfnijIywRgDYTkDA1IU0NMRyHYx4ZKgh+UMDAwMAHYHPWPQsMhRAAAAAElFTkSuQmCC"
FAVICON_PNG_16_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAnElEQVR4nGNkgALV5Nf/GUgAt+eKMjIwMDAwkaMZWQ8jOZqRARMlmhkYGBhYGBgYGNSkmRm2NAoyTN/6jaF//Te45MWpwgyc7IwYmqyL3zG8/vgPYQAuoJ/9loGBgYFhdZUAg7wYM4NZwVsMNRR7YbgZkOnNxXBrjgjDrTkiDFk+XEQZMPAJiXIDYLmKHHB7rigjE4xBjmYGBgYGABaIKTu/xoclAAAAAElFTkSuQmCC"
FAVICON_ICO_BASE64 = "AAABAAIAEBAAAAAAIABgAgAAJgAAACAgAAAAACAA8wAAAIYCAACJUE5HDQoaCgAAAA1JSERSAAAAEAAAABAIBgAAAB/z/2EAAAInSURBVHichZI9a1RBFIafMzM7637c3XwQAy6xigh2AYtY2UQhFklrrQg2+QUW/gf1N6SxS2GzKwREsBK7NFaCAROU7Hf23jtzLG52zQbRFwYGzpxn3vNy5P5Ldcfff70zrrIVs2EELP9WMKWaifm4c6O19EjWn5y0rU+2QtqLIsb8pxkA1Ritb5iQ9jty+/lIQ9pXZ62IKCGCavHQCPwdKeR5UOMTcSEbBmOM7Y0ik0xp1gzWFM2Dc2UwVkTAmgIcYnFfahiJ2TA4I9hJpuxslrlz07F/OOa0q4xTZWvD83CjTJor/bHinZBUhO4o8uZgTJqrNSKQZrC7WWZvp8rqgiHPFQEEyIKyumjY26mye6/MJC8cTeUARKA3UvIAeYCoUL8mvP+Ssn94zt1bjgcbZdqfJzx71WOxJizUDCIXACjmcpYZfQpxy4aVpsFZSCpCa9mQVIQ0uwj6ar5TkLOgFI5C/AOdupwbASDGonDajRz/jFTLQrMmiBTpXwZd1gxQrwrOwovHdU7OIt4Jbz+c8/Eoxbui1qjKbEdmAFXwJTj4NOHrcaBeEbwTlGKEkhV+nEVeH4w4+pbjHXMQWX96mhvBDsbKJJvfxGZNqHghC9AdRsoloV6ZcxGcLdVsSPvaqBarfFkhFsE5C9cXzGwTAdCoxifWhHTQsb4heQhxmvD0TH+6GqJqjMY3JKSDjmmtrWzHfNS2PhEg8H8F6xOJ+ajdWlvZ/g0k+g0JEl7M2gAAAABJRU5ErkJggg=="
APPLE_TOUCH_PNG_BASE64 = FAVICON_PNG_32_BASE64  # Fallback


def _png_response(b64: str) -> Response:
    """Create PNG response from base64 data."""
    data = base64.b64decode(b64)
    resp = make_response(data)
    resp.mimetype = "image/png"
    return _nocache(resp)


@favicon_bp.route("/favicon.ico")
def favicon_ico():
    resp = make_response(base64.b64decode(FAVICON_ICO_BASE64))
    resp.mimetype = "image/x-icon"
    return _nocache(resp)


@favicon_bp.route("/favicon-32.png")
def favicon_png_32():
    return _png_response(FAVICON_PNG_32_BASE64)


@favicon_bp.route("/favicon-16.png")
def favicon_png_16():
    return _png_response(FAVICON_PNG_16_BASE64)


@favicon_bp.route("/apple-touch-icon.png")
@favicon_bp.route("/apple-touch-icon-57x57.png")
@favicon_bp.route("/apple-touch-icon-120x120.png")
@favicon_bp.route("/apple-touch-icon-152x152.png")
@favicon_bp.route("/apple-touch-icon-180x180.png")
def apple_touch_icon():
    return _png_response(APPLE_TOUCH_PNG_BASE64)


@favicon_bp.route("/favicon.svg")
def favicon_svg():
    resp = make_response(FAVICON_SVG)
    resp.mimetype = "image/svg+xml"
    return _nocache(resp)


@favicon_bp.route("/safari-pinned-tab.svg")
def safari_pinned():
    resp = make_response(SAFARI_PINNED_SVG)
    resp.mimetype = "image/svg+xml"
    resp.headers['Content-Type'] = 'image/svg+xml'
    return _nocache(resp)


@favicon_bp.route("/manifest.json")
def manifest():
    manifest_data = {
        "name": "llot - local llm ollama translator",
        "short_name": "llot",
        "description": "Lokalny translator używający Ollama",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f7f8fb",
        "theme_color": "#2563eb",
        "icons": [
            {
                "src": "/apple-touch-icon-57x57.png",
                "sizes": "57x57",
                "type": "image/png"
            },
            {
                "src": "/apple-touch-icon-120x120.png",
                "sizes": "120x120",
                "type": "image/png"
            },
            {
                "src": "/apple-touch-icon-152x152.png",
                "sizes": "152x152",
                "type": "image/png"
            },
            {
                "src": "/apple-touch-icon-180x180.png",
                "sizes": "180x180",
                "type": "image/png"
            }
        ]
    }
    resp = make_response(json.dumps(manifest_data, indent=2))
    resp.mimetype = "application/json"
    return _nocache(resp)