"""Pytest hooks: registers the risk marker and performs dynamic,
risk-threshold-based test selection at collection time."""
import pytest
from framework.risk_engine import RiskEngine

engine = RiskEngine()


def pytest_addoption(parser):
    parser.addoption(
        "--risk-threshold",
        action="store",
        default=None,
        type=int,
        help="Only run tests whose risk area score >= this value. "
             "Defaults to risk_threshold in config/risk_config.yaml.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "risk(area): associate a test with a risk area from risk_config.yaml"
    )


def _risk_area(item):
    marker = item.get_closest_marker("risk")
    return marker.args[0] if marker else None


def pytest_collection_modifyitems(config, items):
    """Dynamic selector: deselect tests below the active risk threshold,
    and order the remaining tests highest-risk-first."""
    override = config.getoption("--risk-threshold")
    threshold = engine.default_threshold if override is None else override

    selected, deselected = [], []
    for item in items:
        area = _risk_area(item)
        if area is None:
            selected.append(item)  # untagged tests always run
            continue
        score = engine.score(area)
        if score >= threshold:
            item._risk_score = score
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)

    # highest risk first; untagged (no score) sink to the bottom
    selected.sort(key=lambda it: getattr(it, "_risk_score", -1), reverse=True)
    items[:] = selected

    print(f"\n[risk-selector] threshold={threshold} "
          f"selected={len(selected)} deselected={len(deselected)}")


@pytest.fixture(scope="session")
def base_url():
    return "https://www.saucedemo.com"
