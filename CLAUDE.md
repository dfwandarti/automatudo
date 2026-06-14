# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automatudo is an E2E test automation framework using **Python + Behave (BDD/Cucumber) + Playwright**. Tests are written in Gherkin (Portuguese), follow Page Object Model (POM), and run against both a local static HTML app and external sites (e.g., Gas Online).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

## Running Tests

```bash
# Run all tests (default device: mobile)
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

The default device is `mobile` (set in `BrowserConfig._default_device`). Override via the `BROWSER_DEVICE` env var.

## Architecture

### Layer overview

```
features/               # Gherkin scenarios (.feature) + step definitions (steps/)
python/
  config/               # BrowserConfig: loads browser_config.json, reads BROWSER_DEVICE env var
  page_field/           # PageField abstraction (see below)
  pages/                # Page Object Model classes (extend BasePage)
  locators/             # CSS/XPath selectors as constants
static/                 # Local HTML pages used as test targets
browser_config.json     # Viewport/device definitions (desktop, mobile, tablet)
```

### PageField system

`PageField` is the core abstraction that bridges Gherkin display names (human-readable strings used in step text) to Playwright locators. The resolution chain is:

1. `DisplayNameToTestId` — checks `display_name_to_test_id.py` mapping, uses `get_by_test_id()`
2. `DisplayNameToXpath` — checks `display_name_to_xpath.py` mapping, uses `locator(xpath)`
3. Raises `ValueError` if unmatched — add the name to one of the mappings

**`PageFieldFactory.from_display_name()`** is the entry point used by common steps and registered as a Behave `ParameterType` named `pageField`. It can return specialized subclasses (`PageFieldEntrar`, `PageFieldLogin`) based on device type or display name, allowing device-specific interaction behavior.

**When to add a new element:**
- Prefer `data-testid` attributes → add to `display_name_to_test_id.py`
- Fallback to XPath → add to `display_name_to_xpath.py`
- Device-specific behavior → subclass `PageField` and register in `PageFieldFactory`

### Common steps

`features/steps/common_steps.py` provides reusable generic steps that work with any display name:

- `Usuário digitou {text} no campo {display_name}`
- `Usuário clica no botão {display_name}`
- `Campo {display_name} terá texto {expected_text}`
- `Input {display_name} terá texto {expected_text}`

These steps use `PageFieldFactory` directly, so no page-specific step code is needed for most interactions. Add page-specific steps only for navigation or logic that doesn't fit the generic pattern.

### Behave context

Set up in `features/environment.py` per-scenario:
- `context.page` — Playwright `Page` instance (use this in steps)
- `context.browser` / `context.playwright` — lifecycle managed by hooks
- `context.device_type` — `"desktop"`, `"mobile"`, or `"tablet"`
