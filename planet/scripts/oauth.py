import os
import re
import random
import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, HTTPError
from webbrowser import open_new
import requests

from requests.auth import HTTPBasicAuth

from .util import generate_nonce, get_claim, duration_human, create_challenge, create_verifier


REDIRECT_URL = 'http://localhost:8080'
SCOPES = 'openid'
PORT = 8080


def get_access_token_from_code(token_uri, client_id, secret, code):
    """
    Parse the access token from Planet's response
    Args:
        uri: the Planet token URI
        client_id: client id
        secret: client secret
        code: authorization code
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

    data_str = "&".join("%s=%s" % (k, v) for k, v in data.items())

    response = requests.post(url='{}?{}'.format(token_uri, data_str), auth=creds, headers={
                             'content-type': 'application/x-www-form-urlencoded'})
    return response.json()


class HTTPServerHandler(BaseHTTPRequestHandler):

    """
    HTTP Server callbacks to handle Planet OAuth redirects
    """

    def __init__(self, request, address, server, token_uri, client_id, secret):
        self.client_id = client_id
        self.secret = secret
        self.token_uri = token_uri
        super().__init__(request, address, server)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if 'code' in self.path and 'state' in self.path:
            self.auth_code = self.path.split('=')[1]
            self.auth_code = self.auth_code.split('&')[0]
            self.server.tokens = get_access_token_from_code(self.token_uri, self.client_id, self.secret,
                                                            self.auth_code)
            if 'expires_in' in self.server.tokens:
                self.wfile.write(bytes(
                    '<html><head><meta http-equiv="refresh" content="0; URL=https://developers.planet.com/quickstart/?fromLogin=true#" /></head><body></body></html>', 'utf-8'))
            else:
                self.wfile.write(
                    bytes('<html><h1>Error fetching access token</h1>'), 'utf-8')
        else:
            self.server.tokens = {}

    # Disable logging from the HTTP Server

    def log_message(self, format, *args):
        return


code_verifier = create_verifier()
code_challenge = create_challenge(code_verifier)


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

    def get_tokens(self):
        """
         Fetches the access key using an HTTP server to handle oAuth
         requests
            Args:
                appId:      The Planet assigned App ID
                appSecret:  The Planet assigned App Secret
        """

        data = {
            'client_id': self._client_id,
            'response_type': 'code',
            'scope': SCOPES,
            'redirect_uri': REDIRECT_URL,
            'state': generate_nonce(),
            'nonce': generate_nonce(10)
        }

        if not self._secret:
            # is the code challenge used for PKCE.
            data['code_challenge'] = code_challenge
            # is the hash method used to generate the challenge, which is always S256.
            data['code_challenge_method'] = 'S256'

        data_str = "&".join("%s=%s" % (k, v) for k, v in data.items())

        auth_server_url = self.metadata['authorization_endpoint'] + '?' + data_str

        open_new(auth_server_url)

        httpServer = HTTPServer(
            ('localhost', PORT),
            lambda request, address, server: HTTPServerHandler(
                request, address, server, self.metadata['token_endpoint'], self._client_id, self._secret))
        httpServer.handle_request()
        return httpServer.tokens

