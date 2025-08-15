import time
import jwt  # PyJWT

# Your Apple Developer info
TEAM_ID = 'QK2FSS3243'         # e.g. 'ABCD1234XY'
KEY_ID = '72F6C4L7BL'           # e.g. '123ABC456D'
AUTH_KEY_PATH = 'Production_APN_Key.p8'  # path to your downloaded .p8 file

def generate_apns_token():
    with open(AUTH_KEY_PATH, 'r') as f:
        secret = f.read()

    headers = {
        'alg': 'ES256',
        'kid': KEY_ID,
    }

    payload = {
        'iss': TEAM_ID,
        'iat': int(time.time())
    }

    token = jwt.encode(
        payload,
        secret,
        algorithm='ES256',
        headers=headers
    )
    return token

if __name__ == "__main__":
    token = generate_apns_token()
    print("Your APNs provider token:\n")
    print(token)
