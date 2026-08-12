"""
Generates the RSA key pair Finance Analytics Platform will use to sign requests to Finvu's
Account Aggregator sandbox (the x-jws-signature header their API requires).

    Private key -> backend/secrets/finvu_private_key.pem
        Stays on this machine. Signs every outgoing request. Never commit
        it, never email it, never put its contents in .env directly.

    Public key (as JWK) -> backend/secrets/finvu_public_key.jwk.json
        This is the ONE file you send to Finvu, so they can verify your
        signatures: email it to support@cookiejar.co.in

Run from the project root (same directory you run uvicorn from):
    python -m backend.scripts.generate_finvu_keys

Re-running is safe - it won't overwrite an existing key pair unless you
pass --force, since generating a new key pair after you've already sent
Finvu your old public key would break signature verification until you
re-register the new one with them.
"""
import argparse
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from joserfc.jwk import RSAKey

from backend.config import settings

# Paths from settings are relative to wherever the app is run from (backend/).
BACKEND_DIR = Path(__file__).resolve().parent.parent
PRIVATE_KEY_PATH = BACKEND_DIR / settings.FINVU_PRIVATE_KEY_PATH
PUBLIC_JWK_PATH = BACKEND_DIR / settings.FINVU_PUBLIC_JWK_PATH


def generate(force: bool = False):
    if PRIVATE_KEY_PATH.exists() and not force:
        print(f"Key pair already exists at {PRIVATE_KEY_PATH}")
        print("Pass --force to overwrite (only do this if you haven't sent")
        print("the old public JWK to Finvu yet, or you're deliberately rotating keys).")
        sys.exit(1)

    PRIVATE_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 1. Generate a 2048-bit RSA key pair (standard for RS256 JWS signing)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # 2. Save the PRIVATE key locally - keep this secret, it's gitignored
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    PRIVATE_KEY_PATH.write_bytes(private_pem)
    PRIVATE_KEY_PATH.chmod(0o600)  # owner read/write only

    # 3. Convert the PUBLIC key to JWK - this is what gets emailed to Finvu
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    jwk = RSAKey.import_key(public_pem)
    jwk_dict = jwk.as_dict(private=False)  # public parts only (n, e)
    jwk_dict.update({"alg": "RS256", "use": "sig", "kid": "finsight-finvu-key-1"})

    PUBLIC_JWK_PATH.write_text(json.dumps(jwk_dict, indent=2))

    print(f"Private key written to: {PRIVATE_KEY_PATH}  (keep secret, gitignored)")
    print(f"Public JWK written to:  {PUBLIC_JWK_PATH}")
    print()
    print(f"Next step: email {PUBLIC_JWK_PATH.name} to support@cookiejar.co.in")
    print("to request your Finvu sandbox client_api_key.")
    print()
    print("Public JWK contents:")
    print(json.dumps(jwk_dict, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite an existing key pair")
    args = parser.parse_args()
    generate(force=args.force)
