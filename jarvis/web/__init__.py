"""Web HUD backend for J.A.R.V.I.S.

Serves an animated Iron-Man-style dashboard and exposes a small JSON API that
reports live system stats and routes typed/spoken commands to J.A.R.V.I.S
skills. Flask is imported lazily by :mod:`jarvis.web.server` so importing this
package never requires it.
"""
