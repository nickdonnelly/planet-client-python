import re
import requests
from requests.auth import HTTPBasicAuth

from urllib.parse import urlparse, parse_qs, urlencode

from http.server import BaseHTTPRequestHandler, HTTPServer

from webbrowser import open_new
from .util import generate_nonce, get_claim, duration_human, create_challenge, create_verifier


REDIRECT_URL = 'http://localhost:8080'
SCOPES = 'openid'
PORT = 8080


def get_access_token_from_code(token_uri, client_id, secret, code, code_verifier):
    """
    Parse the access token from Planet's response
    Args:
        uri: the Planet token URI
        client_id: client id
        secret: client secret
        code: authorization code
        code_verifier: pkce generated code
    Returns:
        a string containing the access key 
    """
    creds = None

    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URL,
        'scope': SCOPES,
        'code': code
    }

    if not secret:
        data['code_verifier'] = code_verifier
        data['client_id'] = client_id
    else:
        creds = HTTPBasicAuth(client_id, secret)

    auth_server_url = token_uri + '?' + urlencode(data)

    response = requests.post(url=auth_server_url, auth=creds, headers={
                             'content-type': 'application/x-www-form-urlencoded'})
    return response.json()


class HTTPServerHandler(BaseHTTPRequestHandler):

    """
    HTTP Server callbacks to handle Planet OAuth redirects
    """

    def __init__(self, request, address, server, token_uri, client_id, secret, code_verifier):
        self.client_id = client_id
        self.secret = secret
        self.token_uri = token_uri
        self.code_verifier = code_verifier
        super().__init__(request, address, server)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        qs = parse_qs(urlparse(self.path).query)

        self.server.tokens = {}

        if 'code' in qs: # Should verify the state also  and 'state' in qs
            self.auth_code = qs['code'][0]
            token_resp = get_access_token_from_code(self.token_uri, self.client_id, self.secret,
                                                            self.auth_code, self.code_verifier)
            if 'access_token' in token_resp:
                self.server.tokens = token_resp
                self.wfile.write(bytes(
                    '<html><head><meta http-equiv="refresh" content="0; URL=https://developers.planet.com/quickstart/?fromLogin=true#" /></head><body></body></html>', 'utf-8'))
            else:
                self.wfile.write(
                    bytes('<html><h1>Unable to complete the authentication flow. Please see the console.</h1>', 'utf-8'))

    # Disable logging from the HTTP Server

    def log_message(self, format, *args):
        return


class TokenHandler:
    """
    Functions used to handle Planet oAuth
    """

    def __init__(self, config):

        url = 'https://{host}/oauth2/{id}/.well-known/oauth-authorization-server'.format(host=config.get('host'),
                                                                                         id=config.get('auth_server_id'))

        self.metadata = requests.get(url=url).json()
        self._client_id = config.get('client_id')
        self._secret = config.get('secret')
        self._code_verifier = create_verifier()

    def get_tokens(self):
        """
         Fetches the access key using an HTTP server to handle oAuth
         requests
        """

        data = {
            'client_id': self._client_id,
            'response_type': 'code',
            'scope': SCOPES,
            'redirect_uri': REDIRECT_URL,
            'state': generate_nonce(),
            'nonce': generate_nonce(10)
        }

        if not self._secret and self._code_verifier:
            # is the code challenge used for PKCE.
            data['code_challenge'] = create_challenge(self._code_verifier)
            # is the hash method used to generate the challenge, which is always S256.
            data['code_challenge_method'] = 'S256'

        query_str = urlencode(data)

        auth_server_url = self.metadata['authorization_endpoint'] + \
            '?' + query_str

        open_new(auth_server_url)

        httpServer = HTTPServer(
            ('localhost', PORT),
            lambda request, address, server: HTTPServerHandler(
                request, address, server, self.metadata['token_endpoint'], self._client_id, self._secret, self._code_verifier))
        httpServer.handle_request()
        return httpServer.tokens
