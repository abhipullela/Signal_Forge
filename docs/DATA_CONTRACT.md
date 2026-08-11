# SignalForge Data Contract

## Raw Record

A raw observation should contain, where available:

- source
- community
- external_id
- text
- timestamp
- engagement metrics

Example:

```json
{
  "source": "example_source",
  "community": "example_community",
  "external_id": "12345",
  "text": "Example post",
  "timestamp": "2026-08-11T10:30:00Z",
  "engagement": {
    "likes": 10,
    "comments": 4,
    "shares": 2
  }
}
