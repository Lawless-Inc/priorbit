"""Sign in once with a free uselawless.com account (OAuth 2.1 + PKCE, dynamic client registration — the same flow
Codex and Claude use). Tokens live in ~/.config/priorbit/credentials.json; refreshed automatically.
An API key (PRIORBIT_API_KEY, or --key) skips all of this."""
import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import time
import urllib.parse
import urllib.request
import webbrowser

CONFIG_DIR = os.environ.get("PRIORBIT_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".config", "priorbit")
CRED_PATH = os.path.join(CONFIG_DIR, "credentials.json")
TIMEOUT = 30


class AuthError(Exception):
    pass


def _get_json(url, data=None, headers=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={"Accept": "application/json", **({"Content-Type": "application/json"} if data is not None else {}), **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())


def _post_form(url, fields):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=body, headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise AuthError(f"token endpoint {e.code}: {e.read().decode()[:300]}") from None


def discover(mcp_url):
    """Resource metadata → authorization server metadata (RFC 9728 / 8414)."""
    base = mcp_url.split("/mcp")[0]
    rm = _get_json(base + "/.well-known/oauth-protected-resource")
    issuer = rm["authorization_servers"][0].rstrip("/")
    for path in ("/.well-known/oauth-authorization-server", "/.well-known/openid-configuration"):
        try:
            return _get_json(issuer + path), rm
        except Exception:  # noqa: BLE001
            continue
    raise AuthError("authorization server metadata not found")


def load_credentials():
    try:
        with open(CRED_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_credentials(c):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    tmp = CRED_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(c, f)
    os.chmod(tmp, 0o600)
    os.replace(tmp, CRED_PATH)


def clear_credentials():
    try:
        os.remove(CRED_PATH)
        return True
    except OSError:
        return False


class _Callback(http.server.BaseHTTPRequestHandler):
    result = {}

    def do_GET(self):  # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _Callback.result = {k: v[0] for k, v in q.items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        ok = "code" in _Callback.result
        self.wfile.write(("<html><body style='font-family:system-ui;padding:40px'><h2>Priorbit: " + ("signed in. You can close this tab." if ok else "sign-in failed: " + _Callback.result.get("error", "?")) + "</h2></body></html>").encode())

    def log_message(self, *a):  # silence
        return


def login(mcp_url, open_browser=True, print_url=print):
    meta, rm = discover(mcp_url)
    srv = http.server.HTTPServer(("127.0.0.1", 0), _Callback)
    port = srv.server_address[1]
    redirect = f"http://127.0.0.1:{port}/callback"
    reg = _get_json(meta["registration_endpoint"], {"client_name": "Priorbit CLI", "redirect_uris": [redirect], "grant_types": ["authorization_code", "refresh_token"],
                                                    "response_types": ["code"], "token_endpoint_auth_method": "none"})
    client_id = reg["client_id"]
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state = secrets.token_urlsafe(16)
    scopes = " ".join(rm.get("scopes_supported") or ["openid", "email", "profile"]) + " offline_access"
    url = meta["authorization_endpoint"] + "?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client_id, "redirect_uri": redirect, "scope": scopes, "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256", "resource": rm.get("resource") or mcp_url})
    t = threading.Thread(target=srv.handle_request, daemon=True)
    t.start()
    print_url(f"Open this URL to sign in (free account):\n{url}\n")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass
    t.join(timeout=600)
    srv.server_close()
    res = _Callback.result
    if not res or "code" not in res:
        raise AuthError("sign-in did not complete: " + (res.get("error_description") or res.get("error") or "timed out"))
    if res.get("state") != state:
        raise AuthError("state mismatch")
    tok = _post_form(meta["token_endpoint"], {"grant_type": "authorization_code", "code": res["code"], "redirect_uri": redirect, "client_id": client_id, "code_verifier": verifier})
    cred = {"issuer": meta.get("issuer"), "token_endpoint": meta["token_endpoint"], "client_id": client_id, "access_token": tok["access_token"],
            "refresh_token": tok.get("refresh_token"), "expires_at": time.time() + int(tok.get("expires_in") or 3600) - 60, "mcp_url": mcp_url}
    save_credentials(cred)
    return cred


def access_token(mcp_url):
    """A valid access token from the store, refreshing when expired. None when not signed in."""
    c = load_credentials()
    if not c:
        return None
    if time.time() < c.get("expires_at", 0):
        return c["access_token"]
    if not c.get("refresh_token"):
        return None
    tok = _post_form(c["token_endpoint"], {"grant_type": "refresh_token", "refresh_token": c["refresh_token"], "client_id": c["client_id"]})
    c.update(access_token=tok["access_token"], refresh_token=tok.get("refresh_token") or c["refresh_token"], expires_at=time.time() + int(tok.get("expires_in") or 3600) - 60)
    save_credentials(c)
    return c["access_token"]
