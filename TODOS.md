# TODOS

## REPL

### Fall back to /bin/sh when the configured shell disappears mid-session

**What:** If the `shell` set in ~/.sawsrc stops existing while saws is running, warn once and retry the command with /bin/sh.

**Why:** `self.shell` is resolved once at startup (`saws/saws.py` `_resolve_shell`). If that binary is removed or moved later (brew/nix upgrade, unmounted volume), every `subprocess.call(..., executable=self.shell)` raises `FileNotFoundError` and every command fails until saws restarts.

**Context:** Found by the adversarial review in /ship of revive/triage (2026-10-11); shipped as a known limitation (user decision). Only affects users who opted into a custom shell. Catch `OSError` around the call in `_process_command`, set `self.shell = None` with one warning, retry. Add a test that points `shell` at a temp executable, deletes it, and runs a command.

**Effort:** S
**Priority:** P2
**Depends on:** None (fits the modernize-ptk3 REPL rewrite)

### `cd` handling swallows commands that start with "cd" (cdk, cdktf)

**What:** Match `cd` only as a whole word in `_handle_cd`.

**Why:** `saws/saws.py` `_handle_cd` uses `stripped_text.startswith('cd')`, so `cdk deploy` (AWS CDK) is treated as `cd k deploy` and never reaches the shell.

**Context:** Pre-existing upstream bug, found by the adversarial review in /ship of revive/triage (2026-10-11). Fix: `stripped_text == 'cd' or stripped_text.startswith('cd ')`, with tests for `cd`, `cd /tmp`, `cdk deploy` and `cdktf synth`.

**Effort:** S
**Priority:** P2
**Depends on:** None (fits the modernize-ptk3 REPL rewrite)

## Packaging

### Remove the unused `__future__` import in data_util.py (upstream #128)

**What:** Drop `from __future__ import print_function` from `saws/data_util.py`.

**Why:** Upstream #128. The plan listed it under the triage PR.

**Context:** Deferred from plan: the fork's revival plan, which listed #128 under the triage PR (user decision D3 in /ship of revive/triage). The modernize-ptk3 PR removes every `from __future__` import, which resolves #128 without touching the line twice.

**Effort:** S
**Priority:** P1
**Depends on:** modernize-ptk3 PR

### Map the remaining support files in the pregate lane config

**What:** Add lanes in `.gstack/pregate.json` for `tests/compat.py`, `tests/__init__.py`, `tests/run_tests.py` and `LICENSE.txt`.

**Why:** gstack's pre-gate cannot trace Python imports, so an edit to one of these files fails the gate with "has no test lane" until it is mapped. It fails closed (nothing slips through), but it blocks /ship on a helper-only change.

**Context:** Found by two reviewers in /ship of revive/triage (2026-10-11); deferred by user decision D7 to avoid a third review cycle. The modernize-ptk3 PR deletes `tests/compat.py` and `tests/run_tests.py`; map `tests/__init__.py` to every test file and `LICENSE.txt` to `[]`.

**Effort:** S
**Priority:** P3
**Depends on:** None

### Publish a Docker image to GHCR (upstream #51)

**What:** A GitHub Actions job that pushes `ghcr.io/bakerbrandond/saws` on version tags.

**Why:** Upstream #51 (11 comments) asks for a way to run saws without installing Python.

**Context:** Pros: one-command trial, `docker run -it ghcr.io/bakerbrandond/saws`. Cons: another pipeline to maintain, and the image is large once AWS CLI v2 is bundled. The Dockerfile builds from source on python:slim (revive/triage). Extend the GitHub Actions CI workflow added by the modernization PR (`.github/workflows/ci.yml`, planned).

**Effort:** M
**Priority:** P3
**Depends on:** A first release tag (v0.5.0)

## Features

### In-REPL profile and region switching (upstream #16, #111)

**What:** Switch AWS profile or region inside saws. Show the current one in the toolbar, pass `AWS_PROFILE`/`AWS_REGION` to child commands, and keep a separate resource cache per profile.

**Why:** This is the most-requested upstream feature. AWS CLI v2 SSO users switch profiles often.

**Context:** Pros: a headline feature for the fork. Cons: resource-cache keying and env propagation add complexity. Start in `saws/toolbar.py`, `saws/keys.py` and `saws/resources.py`.

**Effort:** L
**Priority:** P2
**Depends on:** The awscli-v2 work (the planned `saws/aws_cli.py` CLI adapter and the planned `~/.saws/` resource cache location)

## Completed
