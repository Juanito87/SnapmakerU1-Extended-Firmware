import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG_SCRIPT = REPO_ROOT / "overlays/firmware-extended/65-app-cloud/root/usr/local/bin/octoeverywhere-pkg"
THIRD_PARTY_DOC = REPO_ROOT / "docs/design/third_party.md"
CLOUD_DOC = REPO_ROOT / "docs/cloud.md"
LOCK_FILE = REPO_ROOT / "overlays/firmware-extended/65-app-cloud/root/usr/local/share/octoeverywhere/requirements.lock"
UPDATER_SCRIPT = REPO_ROOT / "scripts/dev/update_octoeverywhere_lock.sh"
WORKFLOW_FILE = REPO_ROOT / ".github/workflows/update_octoeverywhere_lock.yaml"


class OctoEverywherePkgTests(unittest.TestCase):
    def test_installer_uses_commit_pinned_archive(self):
        content = PKG_SCRIPT.read_text()
        self.assertIn('COMMIT="', content)
        self.assertIn('/archive/', content)
        self.assertNotIn('/archive/refs/tags/', content)

    def test_installer_uses_locked_requirements_with_hashes(self):
        content = PKG_SCRIPT.read_text()
        self.assertIn("requirements.lock", content)
        self.assertIn("--require-hashes", content)
        self.assertNotIn("requirements.txt", content)
        self.assertNotIn("install --disable-pip-version-check zstandard", content)

    def test_lock_file_exists_and_pins_hashes(self):
        self.assertTrue(LOCK_FILE.exists(), "requirements.lock must exist")
        content = LOCK_FILE.read_text()
        self.assertIn("--hash=sha256:", content)
        self.assertIn("octowebsocket-client==", content)
        self.assertIn("zstandard==", content)

    def test_docs_describe_commit_and_hash_pinning(self):
        third_party = THIRD_PARTY_DOC.read_text()
        cloud = CLOUD_DOC.read_text()
        self.assertIn("commit", third_party.lower())
        self.assertIn("hash", third_party.lower())
        self.assertIn("commit", cloud.lower())
        self.assertIn("hash", cloud.lower())

    def test_updater_script_exists_and_requires_commit_input(self):
        self.assertTrue(UPDATER_SCRIPT.exists(), "updater script must exist")
        content = UPDATER_SCRIPT.read_text()
        self.assertIn("--commit", content)
        self.assertIn("requirements.lock", content)
        self.assertIn("octoeverywhere-pkg", content)

    def test_workflow_exposes_manual_dispatch_inputs_and_artifacts(self):
        self.assertTrue(WORKFLOW_FILE.exists(), "workflow file must exist")
        content = WORKFLOW_FILE.read_text()
        self.assertIn("workflow_dispatch:", content)
        self.assertIn("commit:", content)
        self.assertIn("version:", content)
        self.assertIn("actions/upload-artifact", content)
        self.assertIn("update_octoeverywhere_lock.sh", content)

    def test_docs_describe_maintainer_refresh_flow(self):
        cloud = CLOUD_DOC.read_text()
        self.assertIn("update_octoeverywhere_lock.sh", cloud)
        self.assertIn("workflow_dispatch", cloud)


if __name__ == "__main__":
    unittest.main()
