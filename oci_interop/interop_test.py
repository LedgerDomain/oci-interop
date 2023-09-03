from oci_interop.wallet_provider import WalletProvider

import dotenv
import logging
import os
import unittest

class InteropTest(unittest.TestCase):
    """
    This is the base class for all test case classes.  It contains common setup and teardown
    logic that handles creation of all the WalletProvider objects.
    """
    @classmethod
    def setUpClass(cls):
        # Load environment variables from .env file, if present.  Never commit .env files to any repository!
        # (`.env` is present in the `.gitignore` file).
        dotenv.load_dotenv()

        # Get log level from environment variable
        log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()

        # Configure logging
        logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        cls.wallet_provider_d = {
            'Spherity': WalletProvider('Spherity'),
            'XATP': WalletProvider('XATP')
        }

    @classmethod
    def tearDownClass(cls):
        pass  # Clean up resources if any
