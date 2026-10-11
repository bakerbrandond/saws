# TODOs

## Publish a Docker image to GHCR (upstream #51)
- **What:** A GitHub Actions job that pushes `ghcr.io/bakerbrandond/saws` on version tags.
- **Why:** Upstream #51 (11 comments) asks for a way to run saws without installing Python.
- **Pros:** One-command trial: `docker run -it ghcr.io/bakerbrandond/saws`.
- **Cons:** Another pipeline to maintain; the image is large once AWS CLI v2 is bundled.
- **Context:** The Dockerfile builds from source on python:slim (revive/triage). Start from `.github/workflows/ci.yml`.
- **Depends on / blocked by:** A first release tag (v0.5.0).

## In-REPL profile and region switching (upstream #16, #111)
- **What:** Switch AWS profile or region inside saws. Show the current one in the toolbar, pass `AWS_PROFILE`/`AWS_REGION` to child commands, and keep a separate resource cache per profile.
- **Why:** This is the most-requested upstream feature. AWS CLI v2 SSO users switch profiles often.
- **Pros:** A headline feature for the fork.
- **Cons:** Resource-cache keying and env propagation add complexity.
- **Context:** Start in `saws/toolbar.py`, `saws/keys.py` and `saws/resources.py`.
- **Depends on / blocked by:** The awscli-v2 work (the `aws_cli` module and the `~/.saws` cache location).
