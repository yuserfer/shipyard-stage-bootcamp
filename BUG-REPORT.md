# BUG-101: renaming a note erases its content

**Reported by:** Priya (release manager) · **Severity:** high (data loss) · **Component:** Notes API

## What happened
I renamed the note "Rollback plan for v1.4" to "Rollback plan for v1.4.1" from the dashboard prototype. The title changed, but the whole rollback procedure in the body is gone. It happened twice.

## Steps (from our support engineer)
```sh
curl -s -X POST localhost:8000/api/notes -d '{"title":"Rollback plan","body":"Redeploy v1.3.2"}'
curl -s -X PATCH localhost:8000/api/notes/1 -d '{"title":"Rollback plan v1.4.1"}'
curl -s localhost:8000/api/notes/1
```

## Expected
Only the title changes. The body is unchanged.

## Actual
`"body": ""`

## Notes
- No error is returned. The API answers `200`.
- Our test suite is green, so nobody noticed.
