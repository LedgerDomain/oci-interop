from oci_interop import logger
from oci_interop.interop_test import InteropTest
from oci_interop.wallet_provider import WalletProvider

from typing import Any

class VRS(InteropTest):
    """
    This class contains test cases for the VRS API.

    TODO: Figure out how to algorithmically iterate over each combination of wallet provider
    and produce a test case for each combination, instead of hard-coding each combination.
    Having them be separate test cases is important because it allows the test runner to
    report on each test case separately.
    """

    def test_vrs_spherity_vp_generate_and_spherity_vp_verify(self):
        test_vrs_vp_generate_and_verify_case(self, vp_generator=self.wallet_provider_d['Spherity'], vp_verifier=self.wallet_provider_d['Spherity'])

    def test_vrs_spherity_vp_generate_and_xatp_vp_verify(self):
        test_vrs_vp_generate_and_verify_case(self, vp_generator=self.wallet_provider_d['Spherity'], vp_verifier=self.wallet_provider_d['XATP'])

    def test_vrs_xatp_vp_generate_and_spherity_vp_verify(self):
        test_vrs_vp_generate_and_verify_case(self, vp_generator=self.wallet_provider_d['XATP'], vp_verifier=self.wallet_provider_d['Spherity'])

    def test_vrs_xatp_vp_generate_and_xatp_vp_verify(self):
        test_vrs_vp_generate_and_verify_case(self, vp_generator=self.wallet_provider_d['XATP'], vp_verifier=self.wallet_provider_d['XATP'])

def test_vrs_vp_generate_and_verify_case(test: Any, *, vp_generator: WalletProvider, vp_verifier: WalletProvider):
    # Generate a VP
    vp_generate_response_json = vp_generator.vrs_vp_generate(
        corr_uuid='5795fefa-3680-4e56-bbd7-ee47ec799ea3',
        credential_type='DSCSAATPCredential'
    )
    test.assertIn('success', vp_generate_response_json, f'{vp_generator.name} failed to generate VP')
    test.assertTrue(vp_generate_response_json['success'], f'{vp_generator.name} failed to generate VP')
    vp = vp_generate_response_json['verifiablePresentation']

    # Verify the VP
    vp_verify_response_json = vp_verifier.vrs_vp_verify(
        vp=vp,
        vp_source=vp_generator.name,
        # Probably doesn't have to be this, but this is a natural choice.
        verifier_did=vp_generator.vrs_holder_did
    )
    # Assert that the VP is valid
    test.assertIn('success', vp_verify_response_json, f'{vp_generator.name}-generated VP failed to verify in {vp_verifier.name}; vp: {vp}, response_json: {vp_verify_response_json}')
    test.assertTrue(vp_verify_response_json['success'], f'{vp_generator.name}-generated VP failed to verify in {vp_verifier.name}; vp: {vp}, response_json: {vp_verify_response_json}')
