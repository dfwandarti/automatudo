# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automatudo is an E2E test automation framework using **Python + Behave (BDD/Cucumber) + Playwright**. Tests are written in Gherkin (Portuguese), follow Page Object Model (POM), and run against a mix of targets:
- Static login pages hosted on GitHub Pages (`https://dfwandarti.github.io/automatudo/static/...`) — the `static/*.html` files in this repo are the source, but scenarios navigate to the *deployed* copy, not `file://`, so HTML changes only take effect in tests after they're pushed and published.
- A live external site (`https://gasonline.galp.com/`).

Beyond standard element interaction/assertion steps, the suite also does pixel-diff visual regression (OpenCV) and YOLO-based logo object-detection, and opportunistically harvests YOLO training data on every element lookup (see below).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

## Running Tests

```bash
# Run all tests
behave

# Run a specific feature file
behave features/login.feature

# Run with a specific device/viewport
BROWSER_DEVICE=desktop behave
BROWSER_DEVICE=mobile behave
BROWSER_DEVICE=tablet behave

# Run with HTML report
behave -f html-pretty -o report.html
```

**Known quirk:** `python/config/browser_config.py` defines `BrowserConfig.get_device_type()` twice. The second definition (which just returns `cls._default_device`, currently `"desktop"`) silently overrides the first (which reads `BROWSER_DEVICE`), so the env var is currently a no-op and every run behaves as `desktop` regardless of what's passed. Keep this in mind before trusting device-specific behavior at runtime — fix by removing the duplicate method if intended.

## Architecture

### Layer overview

```
features/               # Gherkin scenarios (.feature) + step definitions (steps/)
python/
  config/               # BrowserConfig: loads browser_config.json, reads BROWSER_DEVICE env var
  page_field/            # PageField abstraction + display-name mappings (see below)
  pages/                # Page Object Model classes (extend BasePage), one per target site
  yolo/                 # YoloDataset: auto-generates YOLO training data from PageField lookups
static/                 # Local HTML source for the pages served via GitHub Pages
static/snapshots/       # Visual-regression baseline (*_expected.png) and last-run (*_actual.png) images
yolo_dataset/           # Auto-growing YOLO train/val/test images+labels, and custom.yaml class map
yolo_models/            # Trained YOLO weights (*.pt), referenced by common_yolo_steps.py
browser_config.json     # Viewport/device definitions (desktop, mobile, tablet)
```

### PageField system

`PageField` is the core abstraction that bridges Gherkin display names (human-readable strings used in step text) to Playwright locators. The mappings live directly in `python/page_field/` (no separate locators layer). Resolution chain:

1. `DisplayNameToTestId` — checks `display_name_to_test_id.py` mapping, uses `get_by_test_id()`
2. `DisplayNameToXpath` — checks `display_name_to_xpath.py` mapping, uses `locator(xpath)`
3. Raises `ValueError` if unmatched — add the name to one of the mappings

**`PageFieldFactory.from_display_name()`** is the entry point used by common steps and registered as a Behave `ParameterType` named `pageField`. It special-cases two display names into subclasses, everything else gets a plain `PageField`:
- `"login gas online - botão entrar"` + responsive device (`mobile`/`tablet`) → `PageFieldEntrar`, which opens the hamburger menu before clicking.
- `"login - botão logar"` → `PageFieldLogin`, which reads and logs the current username field before clicking (a stand-in for future audit logging).

**When to add a new element:**
- Prefer `data-testid` attributes → add to `display_name_to_test_id.py`
- Fallback to XPath → add to `display_name_to_xpath.py`
- Device-specific behavior → subclass `PageField` and register in `PageFieldFactory`

**Side effect on every lookup:** `PageField.__init__` unconditionally calls `YoloDataset.generate_dataset()` (`python/yolo/yolo_generate_dataset.py`). If the display name is registered in `display_name_to_yolo_class`, it screenshots the page, normalizes the element's bounding box to YOLO label format, and writes an image+label pair into `yolo_dataset/images/{train,val,test}` / `yolo_dataset/labels/{...}` (70/20/10 split). This means every test run touching a tracked element silently grows the training set. **When adding a new YOLO class, update both `display_name_to_yolo_class` and `yolo_dataset/custom.yaml`.**

### Common steps

`features/steps/common_steps.py` provides reusable generic steps that work with any display name:

- `Usuário digitou {text} no campo {display_name}`
- `Usuário clica no botão {display_name}`
- `Campo {display_name} terá texto {expected_text}`
- `Input {display_name} terá texto {expected_text}`

These use `PageFieldFactory` directly, so no page-specific step code is needed for most interactions. Add page-specific steps only for navigation or logic that doesn't fit the generic pattern (see `login_*_steps.py`, which just instantiate a page object and call `navigate_to()`).

### Visual regression (`features/steps/common_image_steps.py`)

Step: `Imagem {display_name} é como esperada`. Screenshots the element's bounding box, diffs it pixel-by-pixel (OpenCV) against `static/snapshots/{display_name}__{device}__expected.png`, tolerating up to 5% differing pixels (`DIFF_THRESHOLD`). The actual screenshot is always written to the matching `*_actual.png` file; on a legitimate visual change, the failure message tips the `cp` command to promote it to the new expected baseline.

### YOLO object detection (`features/steps/common_yolo_steps.py`)

Step: `A imagem {class_name} é encontrada {n} vez(es)`. Runs the model at `YOLO_MODEL_PATH` (`yolo_models/logos-<date>.pt` — update this constant after retraining) on a full-page screenshot and asserts the detected count for a given class name. This is a genuine object-detection assertion, complementary to (and trained by) the pixel-diff approach above.

### Behave context

Set up in `features/environment.py` per-scenario:
- `context.page` — Playwright `Page` instance (use this in steps)
- `context.browser` / `context.playwright` — lifecycle managed by hooks
- `context.device_type` — `"desktop"`, `"mobile"`, or `"tablet"`

`after_all` explicitly flushes/closes the `behave-html-pretty-formatter` (configured in `behave.ini`) so `report.html` is guaranteed to be written even if Behave's own shutdown doesn't do it.
