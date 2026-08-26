# S01E02 browser automation — dry-run first

Midjourney and Suno flows are **not** wired to production credentials in this repo.

## Intended usage

```bash
# Validate prompts before any submission
python3 s01e02-marcianople/automation/validate/validate_prompts.py

# Dry-run: print next actions without browser
python3 s01e02-marcianople/automation/browser/mj_dispatch.py --dry-run

# Live run requires local Playwright profile path (never commit)
export MJ_BROWSER_PROFILE=/path/to/your/profile
python3 s01e02-marcianople/automation/browser/mj_dispatch.py --shot C01
```

Human checkpoints required for: login, CAPTCHA, payment, credit spend, canonical variant selection.

See `canon/remaster-directive.md` §17.
