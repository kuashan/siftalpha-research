from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
DEPLOY = ROOT / "deployment" / "5s-independent-server-module"


class M2ContainerContractTests(unittest.TestCase):
    def test_deployment_files_define_safe_internal_web_contract(self):
        dockerfile = (DEPLOY / "Dockerfile").read_text(encoding="utf-8")
        entrypoint = (DEPLOY / "entrypoint.py").read_text(encoding="utf-8")
        compose = (DEPLOY / "compose.yml").read_text(encoding="utf-8")

        self.assertIn('app.main(host="0.0.0.0", port=8080)', entrypoint)
        self.assertIn("PYTHON_BASE_IMAGE", dockerfile)
        self.assertIn("FIVES_DB_PATH=/data/5s_crypto_v1.db", dockerfile)
        self.assertIn('ENTRYPOINT ["python", "/app/deployment_entrypoint.py"]', dockerfile)
        self.assertIn("expose:", compose)
        self.assertNotIn("\n    ports:", compose)
        self.assertIn("/data", compose)
        self.assertIn("FIVES_IMAGE", compose)
        self.assertIn("no-new-privileges:true", compose)


if __name__ == "__main__":
    unittest.main()
