# Project workflow

The user has authorized committing and pushing completed changes for this project to
https://github.com/Watdafak89/Watdafak.github.io.git on branch main after each coding task.

- Preserve existing local and remote changes. Inspect git status and relevant diffs first.
- Complete the requested work and run checks appropriate to the changes before committing.
- For Python application changes, run `.venv/Scripts/python.exe -m unittest test_app -v`
  on Windows, or the equivalent command in the active Python environment.
- Stage only intended project source, configuration, documentation, and tests.
- Never commit secrets, API keys, `.streamlit/secrets.toml`, `.env`, virtual environments,
  generated documents, or the original backup `app.original.py`.
- Commit with a concise description and push to origin/main. This standing authorization
  applies to future edits too; do not request routine confirmation again.
- Verify that the pushed commit matches the remote main branch and report the result.
- Never force-push or overwrite unrelated remote work. Resolve ordinary conflicts without
  discarding user changes; ask only if intent cannot be determined.
- If authentication or environment permissions block a push, explain the exact blocker.
  Do not claim that a commit was uploaded until verified.
- This is a Streamlit Python app, not a static GitHub Pages site. Secrets for a deployed app
  belong in Streamlit Cloud settings; local secrets are not uploaded.
