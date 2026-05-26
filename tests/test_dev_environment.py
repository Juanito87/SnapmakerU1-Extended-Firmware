import json
import pathlib
import re
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEV_SCRIPT = REPO_ROOT / "dev.sh"
DEV_DOCKERFILE = REPO_ROOT / ".github/dev/Dockerfile"
DEVCONTAINER = REPO_ROOT / ".devcontainer/devcontainer.json"
WORKFLOW = REPO_ROOT / ".github/workflows/dev_environment.yaml"
DEVELOPMENT_DOC = REPO_ROOT / "docs/development.md"


class DevEnvironmentTests(unittest.TestCase):
    def test_devcontainer_reuses_shared_dockerfile(self):
        self.assertTrue(DEVCONTAINER.exists(), "devcontainer.json must exist")
        content = json.loads(DEVCONTAINER.read_text())
        self.assertEqual(content["build"]["context"], "../.github/dev")
        self.assertEqual(content["build"]["dockerfile"], "Dockerfile")
        self.assertEqual(content["workspaceFolder"], "/workspace")

    def test_dev_script_points_to_shared_build_context(self):
        content = DEV_SCRIPT.read_text()
        self.assertIn('IMAGE_NAME="snapmaker-u1-dev"', content)
        self.assertIn('BUILD_CONTEXT=".github/dev"', content)
        self.assertIn('docker build $DOCKER_BUILD_OPTS', content)

    def test_dockerfile_pins_base_image_and_apt_packages(self):
        content = DEV_DOCKERFILE.read_text()
        self.assertRegex(content.splitlines()[0], r"^FROM\s+debian:[^\s]+@sha256:[0-9a-f]{64}$")
        self.assertIn("ARG TARGETARCH", content)
        self.assertIn('detected_arch="$(dpkg --print-architecture)"', content)
        self.assertRegex(content, r'case "\$\{detected_arch\}" in')
        self.assertIn("amd64)", content)
        self.assertIn("arm64)", content)
        self.assertRegex(content, r"libssl-dev:arm64=.*\$\{LIBSSL_DEV_ARM64_VERSION\}")

        packages = [
            "build-essential",
            "cmake",
            "pkg-config",
            "squashfs-tools",
            "git",
            "bc",
            "flex",
            "bison",
            "ca-certificates",
            "libssl-dev",
            "dos2unix",
            "sudo",
            "sshpass",
            "unzip",
            "wget",
            "g++-aarch64-linux-gnu",
            "gcc-aarch64-linux-gnu",
            "file",
            "golang-go",
            "ffmpeg",
            "u-boot-tools",
            "ccache",
            "libssl-dev:arm64",
        ]

        for package in packages:
            self.assertRegex(
                content,
                rf"\b{re.escape(package)}=[^\s\\]+",
                msg=f"{package} must be pinned to an explicit version",
            )

    def test_validation_workflow_checks_dev_environment_contract(self):
        self.assertTrue(WORKFLOW.exists(), "dev environment workflow must exist")
        content = WORKFLOW.read_text()

        self.assertIn("dev.sh", content)
        self.assertIn(".github/dev/Dockerfile", content)
        self.assertIn(".devcontainer/**", content)
        self.assertIn("./dev.sh make tools", content)
        self.assertIn("./dev.sh make firmware", content)
        self.assertIn("devcontainer.json", content)
        self.assertIn("Validate shared Dockerfile wiring", content)
        self.assertIn("matrix:", content)
        self.assertIn("linux/amd64", content)
        self.assertIn("linux/arm64", content)
        self.assertRegex(content, r"runs-on:\s*\$\{\{\s*matrix\.runner\s*\}\}")
        self.assertRegex(content, r"platforms:\s*\$\{\{\s*matrix\.platform\s*\}\}")
        self.assertIn("Dump apt pin diagnostics", content)
        self.assertIn("if: ${{ failure() }}", content)

    def test_docs_explain_devcontainer_and_shared_image(self):
        content = DEVELOPMENT_DOC.read_text()
        self.assertIn("devcontainer", content.lower())
        self.assertIn(".github/dev/Dockerfile", content)
        self.assertIn("./dev.sh", content)


if __name__ == "__main__":
    unittest.main()
