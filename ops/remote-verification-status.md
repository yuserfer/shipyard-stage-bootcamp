Python (`python3 -m unittest discover -s tests -q`): `Ran 54 tests in 1.089s` / `OK`, exit 0.
Dashboard (`node --test "dashboard/tests/*.mjs"`): `ℹ tests 10`, `ℹ pass 10`, `ℹ fail 0`, `ℹ skipped 0`, exit 0.
Probe (`python3 scripts/readiness_probe.py`): `bind address default: 0.0.0.0`, `returned unescaped: True`, `CORS header: *`, `unauthenticated DELETE: HTTP 204`, oversized request `no answer after 2 s`.
Verdict: **RED**. Tests are green, but the probe reproduces F1 (stored XSS), F2 (no auth, open bind and CORS) and F3 (stuck worker); F1 and F2 are High.
Next step: merge fixes 1–3 from `reports/production-readiness.md`, then re-run this probe and expect localhost bind, no CORS header, 401 without a token, and a 413.
