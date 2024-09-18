import requests
import frida
import sys

# Replace these values with your Auth0 configuration
AUTH0_DOMAIN = ''
CLIENT_ID = ''
REALM = ''
AUDIENCE = ''
GRANT_TYPE = "http://auth0.com/oauth/grant-type/password-realm"
USERNAME = ''
PASSWORD = ''

# Endpoint to get tokens
TOKEN_URL = f'https://{AUTH0_DOMAIN}/oauth/token'

# Payload for the token request
payload = {
    'grant_type': GRANT_TYPE,
    'client_id': CLIENT_ID,
    'realm': REALM,
    'audience': AUDIENCE,
    'username': USERNAME,
    'password': PASSWORD,
    'scope': "openid profile email offline_access"
}


def get_tokens():
    try:
        # Make the request to Auth0's /oauth/token endpoint
        response = requests.post(TOKEN_URL, json=payload, verify=False)

        # Raise exception if the request was unsuccessful
        print(response.content)
        response.raise_for_status()

        # Parse response JSON to extract tokens
        tokens = response.json()
        print("Tokens obtained successfully!")
        return tokens['id_token'], tokens['access_token'], tokens['refresh_token']

    except requests.exceptions.RequestException as e:
        print(f"Error getting tokens: {e}")
        return None, None, None


def on_message(message, data):
    if message['type'] == 'error':
        print(f"Frida Error: {message['description']}")
        sys.exit(1)
    else:
        print(f"Message from Frida: {message}")


def run_frida_script():
    session = frida.get_usb_device().attach('APP')

    with open('e.js') as f:
        script_code = f.read()

    script = session.create_script(script_code)
    script.on('message', on_message)
    script.load()
    return script


if __name__ == "__main__":
    script = run_frida_script()
    while True:
        input("Press enter to run\n")
        id_token, access_token, refresh_token = get_tokens()

        if id_token and access_token and refresh_token:
            script.exports_sync.setcredentials(id_token, access_token, refresh_token)
