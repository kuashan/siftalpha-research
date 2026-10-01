import tempfile
import unittest
from pathlib import Path

from storage import StateStore


class StorageTests(unittest.TestCase):
    def test_settings_survive_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.db"
            s = StateStore(path)
            s.seed(["BTCUSDT"], 1, 1000)
            s.set_budget(2500)
            s.set_leverage("BTCUSDT", 7)

            s2 = StateStore(path)
            self.assertEqual(s2.get_budget(), 2500)
            self.assertEqual(s2.get_leverages()["BTCUSDT"], 7)


if __name__ == "__main__":
    unittest.main()
