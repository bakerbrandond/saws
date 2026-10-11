# saws (maintained fork)

Fork of donnemartin/saws, revived in 2026. `origin` is bakerbrandond/saws and
`upstream` is donnemartin/saws. Open PRs against the fork only
(`gh repo set-default bakerbrandond/saws`).

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. Route only to skills in the session's available-skills list; answer directly for quick questions or small scoped edits.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
- Author a backlog-ready spec/issue → invoke /spec

## Testing

Framework: pytest running the unittest-style tests in `tests/` (with `mock`
and `pexpect`). The legacy prompt_toolkit 1.x code asserts a TTY, so run the
suite inside `script` and with output capture off (`-s`); uv supplies Python 3.13 and pinned
runtime and test dependencies, so no virtualenv is needed (bump the pins on
purpose):

```bash
script -qec 'uv run --isolated --python 3.13 --with-editable . --with awscli==1.46.1 --with prompt-toolkit==1.0.18 --with click==6.7 --with configobj==5.0.9 --with pygments==2.21.0 --with six==1.17.0 --with pytest==9.1.1 --with mock==5.2.0 --with pexpect==4.9.0 python -m pytest -q -s -p no:cacheprovider tests' /dev/null
```

Plain `pytest` without a pseudo-terminal reports ~45 false failures
(`assert stdout.isatty()`). `.gstack/pregate.json` maps source files to these
tests for gstack's `/ship` pre-gate.
