from oci_interop.util import get_env_var, jwt_is_expired
from oci_interop import logger

from pathlib import Path
import requests
from typing import Dict, Tuple

class WalletProvider:
    """
    A class that represents a particular account under a wallet provider and manages:
    -   That wallet provider's API URL(s),
    -   The relevant access header for the account under that wallet provider.
    -   The holder DID associated with the account under that wallet provider.
    """

    def __init__(self, name: str):
        """Store only the name and the access header for the wallet provider."""
        self.name = name
        self.access_header = self._get_access_header()

    @property
    def resource_dir_p(self) -> Path:
        """
        Returns the Path to the resource directory for this wallet provider, first
        guaranteeing that the directory exists.
        """
        p = Path(f'resources/{self.name}')
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def vrs_api_url(self) -> str:
        # TODO: Somehow specify different environments (prod, test, dev, etc.)
        if self.name == 'Spherity':
            return get_env_var('SPHERITY_VRS_API_URL')
        elif self.name == 'XATP':
            return get_env_var('XATP_VRS_API_URL')
        else:
            raise ValueError(f'Unknown wallet provider name: {self.name}')

    @property
    def vrs_holder_did(self) -> str:
        # TODO: Somehow specify different environments (prod, test, dev, etc.)
        if self.name == 'Spherity':
            return get_env_var('SPHERITY_VRS_HOLDER_DID')
        elif self.name == 'XATP':
            return get_env_var('XATP_VRS_HOLDER_DID')
        else:
            raise ValueError(f'Unknown wallet provider name: {self.name}')

    def vrs_vp_generate(self, *, corr_uuid: str, credential_type: str) -> Dict:
        """
        Returns the response JSON from the VRS VP generate endpoint.

        Reference curl command:

            curl -X POST <url>/verifiablePresentation/generate -H "<access-header>" -H "Content-Type: application/json" -d '{"corrUUID":"<corr-uuid>", "holderDID":"<holder-did>", "credentialType":"<credential-type>"}'
        """
        headers = {
            self.access_header[0]: self.access_header[1],
            "Content-Type": "application/json"
        }
        body = {
            "corrUUID": corr_uuid,
            "holderDID": self.vrs_holder_did,
            "credentialType": credential_type
        }
        response = requests.post(
            f"{self.vrs_api_url}/verifiablePresentation/generate",
            json=body,
            headers=headers
        )
        response_json = response.json()
        logger.debug(f"VRS VP generate response.json(): {response_json}")
        return response_json

    def vrs_vp_verify(self, vp: str, *, vp_source: str, verifier_did: str) -> Dict:
        """
        Returns the response JSON from the VRS VP verify endpoint.

        Reference curl command:

            curl -X POST <url>/verifiablePresentation/verify -H "<access-header>" -H "Content-Type: application/json" -d '{"verifiablePresentation":"<vp>", "verifierDID":<verifier-did>}'
        """

        headers = {
            self.access_header[0]: self.access_header[1],
            "Content-Type": "application/json",
        }
        body = {
            "verifiablePresentation": vp,
            "verifierDID": verifier_did
        }
        response = requests.post(
            f"{self.vrs_api_url}/verifiablePresentation/verify",
            json=body,
            headers=headers
        )
        response_json = response.json()
        logger.debug(f"{vp_source} VP {vp} -> {self.name} VP verify: response.json(): {response_json}")
        return response_json

    def _get_access_header(self) -> Tuple[str, str]:
        """Returns the access header for the wallet provider, loading it from disk if appropriate."""

        if self.name == 'Spherity':
            return self._get_access_header_spherity()
        elif self.name == 'XATP':
            return self._get_access_header_xatp()
        else:
            raise ValueError(f'Unknown wallet provider name: {self.name}')

    def _get_access_header_spherity(self) -> Tuple[str, str]:
        """
        Attempt to load an existing authn token from disk.  If it exists, check if it's still valid.
        If it doesn't exist, then attempt to retrieve a new authn token from the Spherity authn endpoint.

        Spherity's access header is a bearer token.
        """

        # This logic could be simplified somewhat, but good enough for now.
        access_token: str
        access_token_p = self.resource_dir_p / 'access_token.jwt'
        try:
            if not access_token_p.exists():
                # Note that Spherity imposes a limit of 150 access tokens per 24h.
                access_token = self._get_new_access_token_spherity()
                # Sanity check that the access token is not expired
                assert not jwt_is_expired(access_token)
                # Write the access token to disk
                with access_token_p.open('w') as file:
                    file.write(access_token)
            else:
                with access_token_p.open('r') as file:
                    # Load the access token JWT
                    access_token = file.read()
                    if jwt_is_expired(access_token):
                        # If it's expired, then retrieve a new one.
                        access_token = self._get_new_access_token_spherity()
                        # Sanity check that the access token is not expired
                        assert not jwt_is_expired(access_token)
                        # Write the access token to disk
                        with open(access_token_p, 'w') as file:
                            file.write(access_token)
        except:
            # If anything goes wrong, log the exception, and then re-raise it.
            logger.exception(f'Error retrieving Spherity access token.')
            raise

        # Form the header.
        return ('Authorization', f'Bearer {access_token}')

    @staticmethod
    def _get_new_access_token_spherity() -> str:
        """
        Note that Spherity imposes a limit of 150 access tokens per 24h.

        Reference curl command:

           curl -X POST https://auth.caro.vc/oauth/token -H "Content-Type: application/json" -d '{ "audience": "https://api.caro.vc/", "grant_type": "client_credentials", "client_id": "<client-id-here>", "client_secret": "<client-secret-here>" }'
        """

        logger.info('Retrieving new Spherity access token.')

        # Read the client ID and secret from the environment variables
        client_id = get_env_var('SPHERITY_CLIENT_ID')
        client_secret = get_env_var('SPHERITY_CLIENT_SECRET')

        headers = { "Content-Type": "application/json" }
        body = {
            "audience": "https://api.caro.vc/",
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        response = requests.post(
            "https://auth.caro.vc/oauth/token",
            json=body,
            headers=headers
        )
        response_json = response.json()
        logger.debug(f"Spherity login response.json(): {response_json}")
        return response_json['access_token']

    def _get_access_header_xatp(self) -> Tuple[str, str]:
        """XATP's access header is an API key."""

        xatp_api_key = get_env_var('XATP_API_KEY')
        return ('X-API-Key', xatp_api_key)
