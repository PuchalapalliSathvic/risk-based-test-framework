"""Standalone CLI: preview risk scores and what the selector would run.

Usage:
    python -m framework.report                 # use config threshold
    python -m framework.report --threshold 15  # override
"""
import argparse
from framework.risk_engine import RiskEngine


def main():
    parser = argparse.ArgumentParser(description="Risk selection preview")
    parser.add_argument("--threshold", type=int, default=None)
    args = parser.parse_args()

    engine = RiskEngine()
    threshold = engine.default_threshold if args.threshold is None else args.threshold

    print(f"Active risk threshold: {threshold}\n")
    print(f"{'RISK AREA':<20}{'SCORE':<8}{'SELECTED'}")
    print("-" * 40)
    for area, score in engine.ranked():
        mark = "YES" if score >= threshold else "no"
        print(f"{area:<20}{score:<8}{mark}")


if __name__ == "__main__":
    main()
