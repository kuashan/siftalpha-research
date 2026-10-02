import unittest

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


if __name__ == "__main__":
    unittest.main()
