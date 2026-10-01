import os
import unittest
from unittest.mock import patch

from config import Settings


class ConfigTests(unittest.TestCase):
    def test_testnet_mode_requires_explicit_value(self):
        with patch.dict(os.environ, {"FIVES_MODE": "TESTNET"}, clear=False):
            self.assertEqual(Settings.from_env().mode, "TESTNET")

    def test_live_is_not_admitted(self):
        with patch.dict(os.environ, {"FIVES_MODE": "LIVE"}, clear=False):
            self.assertEqual(Settings.from_env().mode, "PAPER")

    def test_credentials_presence_is_boolean_only(self):
        with patch.dict(
            os.environ,
            {
                "FIVES_MODE": "TESTNET",
                "BINANCE_TESTNET_API_KEY": "key",
                "BINANCE_TESTNET_API_SECRET": "secret",
            },
            clear=False,
        ):
            self.assertTrue(Settings.from_env().testnet_credentials_present)


if __name__ == "__main__":
    unittest.main()
