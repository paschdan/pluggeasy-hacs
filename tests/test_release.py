"""Keep release metadata consistent with the Home Assistant integration."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseConfigurationTests(unittest.TestCase):
    """Verify the HACS version updater and release version sources."""

    def test_version_sources_match(self) -> None:
        """The release tracker, simple strategy, and HACS share a version."""
        tracker = json.loads((ROOT / ".release-please-manifest.json").read_text())
        integration = json.loads(
            (ROOT / "custom_components/pluggeasy/manifest.json").read_text()
        )

        self.assertEqual(tracker["."], integration["version"])
        self.assertEqual((ROOT / "version.txt").read_text().strip(), tracker["."])

    def test_updates_integration_version_only(self) -> None:
        """Releases bump the integration, not its pinned device dependency."""
        config = json.loads((ROOT / "release-please-config.json").read_text())

        self.assertEqual(
            config["packages"]["."]["extra-files"],
            [
                {
                    "type": "json",
                    "path": "custom_components/pluggeasy/manifest.json",
                    "jsonpath": "$.version",
                }
            ],
        )

    def test_preserves_release_tag_scheme(self) -> None:
        """Continue the existing v0.6.4-style tags understood by HACS."""
        config = json.loads((ROOT / "release-please-config.json").read_text())
        package = config["packages"]["."]

        self.assertEqual(package["release-type"], "simple")
        self.assertFalse(package["include-component-in-tag"])
        self.assertTrue(package["include-v-in-tag"])
