# Risk-Based Test Automation Framework

Most test suites treat every test as equally important. In practice they aren't. A broken login or a broken checkout costs you real money and real users, while a misaligned footer link does not. This framework acts on that difference. It scores each area of the application by how risky it is, and then runs tests in priority order, dropping the low-risk ones entirely when you only have time for the critical path.

The whole thing is built around one idea: **risk is data you configure, not logic you hard-code.** You tune priorities in a YAML file, tag each test with the area it covers, and the framework works out what to run and in what order.

Stack: Python, Pytest, and Playwright, organized with the Page Object Model.

## Table of contents

- [The problem this solves](#the-problem-this-solves)
- [The mock application](#the-mock-application)
- [Risk areas and how they're scored](#risk-areas-and-how-theyre-scored)
- [How risk turns into a test run](#how-risk-turns-into-a-test-run)
- [Project layout](#project-layout)
- [Setup](#setup)
- [Running it](#running-it)
- [Reading the output](#reading-the-output)
- [Extending the framework](#extending-the-framework)
- [Design decisions](#design-decisions)
- [Known limitations](#known-limitations)

## The problem this solves

Say you have a regression suite of a few hundred tests and a CI window that only comfortably fits a fraction of them on every commit. You have two bad options: run everything and wait, or pick a subset by hand and hope you picked the right ones. Both get worse as the suite grows.

Risk-based testing gives you a third option. You decide once, in config, how risky each part of the app is. From then on the framework runs the riskiest tests first, and can cut off everything below a threshold you set per run. High threshold gives you a fast smoke check of the things that would hurt most if they broke. Low threshold gives you the full sweep. Same suite, same code, one number changes.

## The mock application

Tests run against [SauceDemo](https://www.saucedemo.com), a public demo storefront that Sauce Labs keeps online specifically for automation practice. It stands in for a real e-commerce site and has all the pieces you'd want to exercise:

- a login page with several test accounts (including a deliberately locked-out one)
- a product catalog of six items with sorting
- a shopping cart
- a multi-step checkout with an order summary and confirmation

Using a stable public site means anyone who clones this repo can run the tests immediately, with no app to stand up or seed first.

## Risk areas and how they're scored

I broke the app into five functional areas and scored each one. The scoring model is the standard risk formula:

```
risk score = likelihood x impact
```

Both factors are rated 1 to 5, so scores land somewhere between 1 and 25. **Likelihood** is how prone that area is to defects (complex, frequently changed code scores higher). **Impact** is how much damage a failure there does to the business or the user.

| Risk area          | Likelihood | Impact | Score | Why it's scored this way                                                      |
|--------------------|:----------:|:------:|:-----:|------------------------------------------------------------------------------|
| `authentication`   | 4          | 5      | 20    | If login breaks, nobody gets in. Also the obvious security surface.          |
| `checkout_payment` | 4          | 5      | 20    | A broken checkout means orders don't complete, which is lost revenue.        |
| `product_catalog`  | 3          | 4      | 12    | The main way users find things. Degraded but not a hard blocker.             |
| `cart_management`  | 3          | 3      | 9     | Matters, but a cart glitch is usually recoverable and lower blast radius.    |
| `static_content`   | 2          | 1      | 2     | Footer links and cosmetic text. Worth a test, never worth blocking a release.|

Every one of these numbers lives in [`config/risk_config.yaml`](config/risk_config.yaml). Nothing in the test code hard-codes a score, so re-prioritizing is a config edit, not a code change. That file also holds the default threshold:

```yaml
risk_threshold: 12   # tests at or above this score run by default
```

At the default of 12, the three highest areas run and the two lowest are skipped. Raise it and you tighten to the critical path. Drop it to 0 and everything runs.

## How risk turns into a test run

There are three moving parts, and it's worth understanding how they hand off to each other.

**1. Tests declare their area.** Each test is tagged with a decorator that names the risk area it covers:

```python
@risk("authentication")
def test_valid_login(login_page):
    ...
```

That's the only thing a test author has to think about. No scores in the test, just which area it belongs to.

**2. The risk engine owns the scoring.** `framework/risk_engine.py` reads the YAML once and answers questions about it: what's the score for this area, what's the default threshold, what's the full ranking. It's deliberately small and has no idea Pytest exists, which makes it easy to reuse (the reporting CLI leans on the exact same engine).

**3. A Pytest hook does the selecting.** This is where it comes together. Pytest has a hook called `pytest_collection_modifyitems` that fires after it discovers all the tests but before it runs any. The framework hooks in there (`conftest.py`) and, for each collected test:

- reads its `@risk(...)` tag
- asks the engine for that area's score
- keeps it if the score meets the threshold, deselects it if not
- (tests with no tag always run, so nothing gets silently dropped by accident)

Then it sorts whatever survived so the highest-risk tests run first. Deselected tests show up in Pytest's normal "deselected" count, exactly as if you'd filtered them with a marker expression.

The reason this is a collection hook and not a wrapper script matters: because selection happens through Pytest's own machinery, everything else in the Pytest ecosystem still works unchanged. You can combine it with `-k`, run in parallel with `pytest-xdist`, plug it into any CI runner, and it behaves. A homegrown "run these files" script would throw all of that away.

## Project layout

```
risk-based-framework/
├── config/
│   └── risk_config.yaml      # Risk weights and the default threshold. The one file you tune.
├── framework/
│   ├── risk_engine.py        # Loads config, computes scores, exposes the ranking.
│   ├── markers.py            # The @risk("area") decorator.
│   ├── driver.py             # Playwright browser setup and teardown.
│   └── report.py             # CLI to preview scores and selection without running tests.
├── pages/                    # Page Object Model. One file per screen.
│   ├── base_page.py          # Shared navigation and helpers.
│   ├── login_page.py
│   ├── inventory_page.py
│   └── checkout_page.py
├── tests/
│   ├── fixtures.py           # Browser and page-object fixtures.
│   └── test_shop.py          # The sample tests, each tagged with @risk(...).
├── conftest.py               # The dynamic selector hook and the --risk-threshold option.
├── pytest.ini                # Pytest config and marker registration.
└── requirements.txt
```

## Setup

You'll need Python 3.9 or newer.

```bash
# Get the code
git clone <YOUR_REPO_URL>.git
cd risk-based-framework

# Install the Python dependencies
pip install -r requirements.txt

# Install the actual browser Playwright drives
playwright install chromium
```

That last step is easy to forget. Playwright the Python package and the browser binary it controls are installed separately, and the tests won't run without the browser.

## Running it

**Preview what would run, without launching a browser:**

```bash
python -m framework.report
```

This prints the score table and marks what's selected at the current threshold. It's pure Python with no browser involved, so it's a fast way to sanity-check your config or see how a threshold change plays out:

```bash
python -m framework.report --threshold 20
```

**Run the tests:**

```bash
pytest                        # default threshold from config (12): runs the top 4 tests
pytest --risk-threshold 20    # critical path only: 3 tests
pytest --risk-threshold 0     # full regression: all 6 tests
```

One thing to watch: run these from the repo root, the folder that has `pytest.ini`. If you run from somewhere else, Pytest won't load the config or the `conftest.py` selector, and you'll either see import errors or the selection simply won't happen. If tests blow up immediately on imports, that's almost always why.

## Reading the output

Every run prints a one-line summary of what the selector did, right at the top:

```
[risk-selector] threshold=12 selected=4 deselected=2
collected 6 items / 2 deselected / 4 selected
```

The first line is the framework talking. The second is Pytest's own accounting, and the two should always agree on the numbers. Below that you get the normal Pytest run, with the selected tests executing highest-risk-first.

The `report` command shows the same decision as a table:

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

## Extending the framework

The design goal was that day-to-day changes shouldn't require touching the engine or the hook. In practice:

**Add a new test:** write it in `tests/`, tag it with `@risk("some_area")`, done. The selector picks it up automatically.

**Add a new risk area:** add an entry under `risk_areas` in the YAML with its likelihood and impact. No code change.

**Re-prioritize:** change the likelihood or impact numbers in the YAML. The next run reflects it. This is the whole point, priorities shift over time and you shouldn't have to touch tests to follow them.

**Change what "critical" means for a run:** set `--risk-threshold` on the command line, or move the default in the config.

**Add a new page:** create a page object in `pages/` that extends `BasePage`, and expose a fixture for it in `tests/fixtures.py`.

## Design decisions

A few choices worth explaining, since they were deliberate.

**Risk lives in config, not code.** A product owner or QA lead can re-rank the whole suite by editing a YAML file, without reading Python. Keeping the numbers out of the tests is what makes the priorities something the team can own together.

**The selector is a real Pytest hook.** I went out of my way not to build a custom test runner. Riding on `pytest_collection_modifyitems` means the framework inherits everything Pytest already does well and composes with the rest of its ecosystem instead of fighting it.

**Page Object Model for the UI.** Selectors and page actions live in one place per screen. When SauceDemo changes a button, one page object changes and every test that used it keeps working. The tests read as intent (`login`, `add_backpack_to_cart`) rather than a pile of CSS selectors.

**The engine doesn't know about Pytest.** `risk_engine.py` is plain Python with a single job. That separation is why the reporting CLI can reuse it directly, and why it'd be straightforward to drive selection from something other than Pytest later if you ever needed to.

**Graceful import when Playwright is missing.** `driver.py` doesn't hard-crash on import if the browser isn't installed. That keeps the `report` CLI and the engine usable in environments where you haven't set up a browser, which is handy in CI stages that only need the risk preview.

## Known limitations

Being straight about the edges of the prototype:

- **Equal scores don't have a strict tie-break.** `authentication` and `checkout_payment` both score 20, so between the two of them the order falls back to collection order rather than something deterministic. If you need a guaranteed ordering between equal-risk areas, nudge one factor so the scores differ.
- **Risk scores are static.** They come straight from config. A natural next step is to feed in signals like recent code churn, historical failure rate, or which files a commit touched, and let those adjust the scores automatically.
- **One test maps to one area.** The `@risk` decorator takes a single area. A test that genuinely spans two areas has to pick the dominant one. Multi-area tagging would be a reasonable extension.
- **The sample suite is small on purpose.** Six tests is enough to demonstrate selection clearly. The mechanism doesn't change as the suite grows, it just gets more useful.