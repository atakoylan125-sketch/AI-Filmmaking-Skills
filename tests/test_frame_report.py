import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/staging-with-manimgx/scripts/staging_render.py"
MODULE_SPEC = importlib.util.spec_from_file_location("staging_render", SCRIPT)
renderer = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = renderer
MODULE_SPEC.loader.exec_module(renderer)


class FrameReportTests(unittest.TestCase):
    def frame_for(self, scene):
        spec = renderer.Spec(scene)
        with patch.object(renderer, "SPEC", spec):
            return renderer.frame_report(spec.shots[0])

    def test_north_facing_camera_uses_screen_left_and_right(self):
        frame = self.frame_for({
            "characters": [
                {"name": "west", "pos": [-1, 3]},
                {"name": "east", "pos": [1, 3]},
            ],
            "shots": [{
                "target": ["west", "east"],
                "pos": [0, 0],
                "dir": 90,
                "lens": 24,
            }],
        })

        self.assertEqual(
            {item["ref"]: item["side"] for item in frame["in_view"]},
            {"west": "left", "east": "right"},
        )
        self.assertEqual([item["ref"] for item in frame["in_view"]], ["west", "east"])

    def test_light_direction_labels(self):
        frame = self.frame_for({
            "characters": [{"name": "subject", "pos": [0, 0]}],
            "lights": [
                {"name": "front", "direction": 90},
                {"name": "back", "direction": 270},
                {"name": "left", "direction": 180},
                {"name": "right", "direction": 0},
            ],
            "shots": [{"target": "subject", "pos": [0, -2], "dir": 90, "lens": 24}],
        })

        self.assertEqual(
            frame["lights"],
            [
                {"name": "front", "from": "into-lens"},
                {"name": "back", "from": "behind-camera"},
                {"name": "left", "from": "frame-left"},
                {"name": "right", "from": "frame-right"},
            ],
        )

    def test_includes_move_endpoints_and_point_props_but_skips_bands(self):
        frame = self.frame_for({
            "characters": [{
                "name": "mover",
                "pos": [0, 2],
                "moves": [{"to": [0, 3]}],
            }],
            "props": [
                {"type": "rect", "name": "table", "pos": [0.5, 2]},
                {"type": "band", "name": "strip", "points": [[-1, 1], [1, 1]]},
            ],
            "shots": [{"target": "mover", "pos": [0, 0], "dir": 90, "lens": 24}],
        })

        self.assertEqual(
            {item["ref"] for item in frame["in_view"]},
            {"mover", "mover@1", "table"},
        )
        self.assertNotIn("strip", frame["out_of_view"])


if __name__ == "__main__":
    unittest.main()
