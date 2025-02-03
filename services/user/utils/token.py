import jwt
import datetime

SECRET_KEY = "mysecretkey"  # Change this to a secure key


def create_jwt(payload: dict, expires_in=3600):
    expiration = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
    payload["exp"] = expiration  # Add expiration
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_jwt(token: str):
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"


def is_token_valid(token: str) -> bool:
    response = decode_jwt(token)
    if "Token has expired" not in response and "Invalid token" not in response:
        return True
    return False


# # Example Usage
# token = create_jwt({"user_id": 123})
# print("Generated Token:", token)

# decoded = decode_jwt(token)
# print("Decoded Payload:", decoded)
