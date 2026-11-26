# Space Knights Field Manual (phone app)

An installable, offline phone app version of the Space Knights Field Manual,
hosted free on GitHub Pages.

- `index.html`, `sw.js`: built files, don't edit by hand.
- `tools/field-manual-source.html`: the offline Field Manual this is built from.
- `tools/build.py`: rebuilds the app. When the rules change:
  `python3 tools/build.py path/to/Space_Knights_Field_Manual_offline.html`, then commit and push.
  Phones pick up the new version the next time the app is opened online.

Saved armies and scenarios stay on each phone. Use army codes (SK1:) and
scenario codes (SKS1:) to share them.
