# S01E02 browser automation — dry-run first

Midjourney live runs are handled by the **agent bus** on Evan's laptop.

**Start here:** [`../agent-bus/BROWSER-AGENT.md`](../agent-bus/BROWSER-AGENT.md)

## Intended usage

```bash
# Validate prompts before any submission
python3 s01e02-marcianople/automation/validate/validate_prompts.py

# Queue a request for the browser agent
python3 s01e02-marcianople/automation/ingest/queue_mj_request.py --shot H06

# Dry-run stub (legacy)
python3 s01e02-marcianople/automation/browser/mj_dispatch.py --shot C01
```

Human checkpoints required for: login, CAPTCHA, payment, credit spend, canonical variant selection.

See `canon/remaster-directive.md` §17.
