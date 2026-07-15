"""Risk engine: loads risk config, computes scores, drives dynamic selection."""
import os
import yaml

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "risk_config.yaml"
)


class RiskEngine:
    def __init__(self, config_path=_CONFIG_PATH):
        with open(config_path, "r") as fh:
            self._cfg = yaml.safe_load(fh)
        self.default_threshold = self._cfg.get("risk_threshold", 0)
        self._areas = self._cfg.get("risk_areas", {})

    def score(self, area):
        """Return likelihood * impact for a named risk area."""
        if area not in self._areas:
            raise KeyError(f"Unknown risk area: {area}")
        a = self._areas[area]
        return a["likelihood"] * a["impact"]

    def all_scores(self):
        return {area: self.score(area) for area in self._areas}

    def is_selected(self, area, threshold=None):
        """True if the area's risk score meets/exceeds the threshold."""
        t = self.default_threshold if threshold is None else threshold
        return self.score(area) >= t

    def ranked(self):
        """Areas sorted high-to-low risk, as (area, score) tuples."""
        return sorted(self.all_scores().items(), key=lambda kv: kv[1], reverse=True)
