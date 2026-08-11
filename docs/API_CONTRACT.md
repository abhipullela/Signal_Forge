# SignalForge API Contract

## GET /api/v1/signals

Returns ranked signals.

Potential response:

```json
{
  "signals": [
    {
      "id": 1,
      "label": "Example Trend",
      "signal_score": 87.4,
      "confidence": 0.91,
      "growth_rate": 2.4,
      "community_count": 6
    }
  ]
}
