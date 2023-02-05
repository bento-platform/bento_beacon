import json
import requests
import os
import jwt

from flask import request
from jwt.algorithms import RSAAlgorith
m
from .exceptions import AuthXException

class AuthxMiddleware():
    def __init__(self):
        print('middleware initialized')
        # authx poc
        # TODO: cleanup ---
        self.OIDC_ISSUER = os.getenv('OIDC_ISSUER', "https://localhost/auth/realms/realm")
        self.CLIENT_ID = os.getenv('CLIENT_ID', "abc123") 

        self.OIDC_WELLKNOWN_URL = self.OIDC_ISSUER + "/protocol/openid-connect/certs"

        self.OIDC_ALG="RS256" 

        r =requests.get(self.OIDC_WELLKNOWN_URL, verify=False)
        jwks = r.json()

        public_keys = jwks["keys"]
        rsa_key = [x for x in public_keys if x["alg"] == self.OIDC_ALG][0]
        rsa_key_json_str = json.dumps(rsa_key)
        
        self.public_key = RSAAlgorithm.from_jwk(rsa_key_json_str)
        # ---

    def verify_token(self):
        print("authx checkup")
        if request.headers.get("Authorization"):
            print("authz header discovered")
            # Assume is Bearer token
            authz_str_split=request.headers.get("Authorization").split(' ')
            if len(authz_str_split) > 1:
                token_str = authz_str_split[1]
                # print(token_str)

                # use idp public_key to validate and parse inbound token
                try:
                    payload = jwt.decode(token_str, self.public_key, algorithms=[self.OIDC_ALG], audience="account")
                    header = jwt.get_unverified_header(token_str)
                except jwt.exceptions.ExpiredSignatureError:
                    raise AuthXException('Expired access_token!')
                except Exception:
                    raise AuthXException('access_token error!')

                # print(json.dumps(header, indent=4, separators=(',', ': ')))
                # print(json.dumps(payload, indent=4, separators=(',', ': ')))
            
                # TODO: parse out relevant claims/data
                roles = payload["resource_access"][self.CLIENT_ID]["roles"]
                print(roles)

            else:
                raise AuthXException('Malformed access_token !')
        else:
            raise AuthXException('Missing access_token !')