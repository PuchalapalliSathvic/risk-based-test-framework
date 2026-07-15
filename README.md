# Risk-Based Test Automation Framework

A prototype test automation framework that **dynamically selects and prioritizes
tests based on risk**. Instead of running an entire suite blindly, it scores each
functional area by *likelihood × impact*, then runs only the tests whose risk
meets a configurable threshold, ordered highest-risk-first.

Built with **Python + Pytest + Playwright**, using the **Page Object Model**.

---

## 1. Mock Application & Risk Areas

The framework tests **[SauceDemo](https://www.saucedemo.com)**, a public mock
e-commerce web app (login, product catalog, cart, checkout). It's used as a
stand-in for a real online store.

Five distinct risk areas are identified, each scored on two 1–5 factors:

| Risk Area           | Likelihood | Impact | **Score** | Rationale                                   |
|---------------------|:----------:|:------:|:---------:|---------------------------------------------|
| `authentication`    | 4          | 5      | **20**    | Security-critical; blocks all access        |
| `checkout_payment`  | 4          | 5      | **20**    | Revenue-critical; broken orders = lost sales|
| `product_catalog`   | 3          | 4      | **12**    | Core discovery path                         |
| `cart_management`   | 3          | 3      | **9**     | Important but recoverable                    |
| `static_content`    | 2          | 1      | **2**     | Cosmetic; low priority                       |

> **Risk score = likelihood × impact** (range 1–25). Higher = tested first and
> more often.

All values live in [`config/risk_config.yaml`](config/risk_config.yaml) and can
be edited without touching test code.

---

## 2. Framework Structure

```
risk-based-framework/
├── config/
│   └── risk_config.yaml      # Risk weights + default threshold (the "knobs")
├── framework/
│   ├── risk_engine.py        # Loads config, computes scores, selection logic
│   ├── markers.py            # @risk("area") decorator
│   ├── driver.py             # Playwright setup/teardown
│   └── report.py             # CLI: preview scores & selection
├── pages/                    # Page Object Model
│   ├── base_page.py
│   ├── login_page.py
│   ├── inventory_page.py
│   └── checkout_page.py
├── tests/
│   ├── fixtures.py           # Browser + page-object fixtures
│   └── test_shop.py          # Sample tests, each tagged with @risk(...)
├── conftest.py               # Dynamic selector (collection hook)
├── pytest.ini
└── requirements.txt
```

### How dynamic selection works

1. Each test is tagged with a risk area: `@risk("authentication")`.
2. At collection time, `conftest.py`'s `pytest_collection_modifyitems` hook asks
   the `RiskEngine` for each test's score.
3. Tests scoring **below the active threshold are deselected**; the rest are
   **reordered highest-risk-first**.
4. The threshold defaults to `risk_config.yaml` but can be overridden per run
   with `--risk-threshold`.

This means the same suite can run as a **fast critical-path smoke check**
(high threshold) or a **fuller regression run** (low threshold), driven entirely
by config.

---

## 3. Setup

```bash
# 1. Clone and enter
git clone <YOUR_REPO_URL>.git
cd risk-based-framework

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install the Playwright browser
playwright install chromium
```

---

## 4. Running

### Preview the risk selection (no browser needed)

```bash
python -m framework.report
```
```
Active risk threshold: 12

RISK AREA           SCORE   SELECTED
----------------------------------------
authentication      20      YES
checkout_payment    20      YES
product_catalog     12      YES
cart_management     9       no
static_content      2       no
```

Override the threshold to see it change:
```bash
python -m framework.report --threshold 20
```

### Run the tests with dynamic selection

```bash
# Default: runs tests at/above the config threshold (12), highest-risk-first
pytest

# Critical-path only: raise the bar to 20
pytest --risk-threshold 20

# Full regression: lower the bar so everything runs
pytest --risk-threshold 0
```

Example output header:
```
[risk-selector] threshold=12 selected=4 deselected=2
collected 6 items / 2 deselected / 4 selected
```

---

## 5. How to Extend

- **Add a risk area:** add an entry to `risk_config.yaml`.
- **Add a test:** write it in `tests/`, tag it with `@risk("your_area")`.
- **Re-tune priorities:** change `likelihood`/`impact` in the YAML — no code
  changes required.
- **Change what "critical" means:** adjust `risk_threshold` or pass
  `--risk-threshold`.

---

## Design Notes

- **Page Object Model** isolates selectors/actions from test logic, so UI changes
  touch one file.
- **Risk config is data, not code**, so non-engineers can re-prioritize.
- The **selector is a standard pytest hook**, so it composes with `-k`, markers,
  parallel runners (`pytest-xdist`), and CI unchanged.
- `driver.py` degrades gracefully if Playwright isn't installed, keeping the repo
  importable for the `report` CLI and unit-level checks.
