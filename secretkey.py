import secrets

# Generate a 50-character random secret key
secret_key = secrets.token_urlsafe(64)
print(secret_key)