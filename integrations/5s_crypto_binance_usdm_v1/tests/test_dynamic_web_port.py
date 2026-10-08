import unittest
from unittest.mock import patch

import app


class DynamicWebPortTests(unittest.TestCase):
    def test_port_zero_allocates_available_loopback_port(self):
        server = app.create_server("127.0.0.1", 0)
        try:
            host, port = server.server_address[:2]
            self.assertEqual(host, "127.0.0.1")
            self.assertGreater(int(port), 0)
            self.assertLessEqual(int(port), 65535)
        finally:
            server.server_close()

    def test_start_gate_refreshes_recovery_before_enabling(self):
        summary = {"status": "PASS", "symbols": {"BTCUSDT": {"status": "PASS"}}}
        with patch.object(app.testnet_session, "credentials", return_value=("key", "secret")), \
                patch.object(app, "run_m4_recovery", return_value=summary) as recovery:
            app.ensure_symbol_reconciled_for_start("BTCUSDT")
        recovery.assert_called_once_with()

    def test_start_gate_rejects_unreconciled_symbol(self):
        summary = {"status": "BLOCKED", "symbols": {"BTCUSDT": {"status": "BLOCKED"}}}
        with patch.object(app.testnet_session, "credentials", return_value=("key", "secret")), \
                patch.object(app, "run_m4_recovery", return_value=summary):
            with self.assertRaisesRegex(ValueError, "恢复对账未通过"):
                app.ensure_symbol_reconciled_for_start("BTCUSDT")


if __name__ == "__main__":
    unittest.main()
