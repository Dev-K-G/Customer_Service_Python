from prometheus_client import Counter

class Metrics:
    # Counts how many times rate limits are exceeded
    RATE_LIMIT_HITS = Counter(
        "rate_limit_exceeded_total",
        "Total number of requests blocked by rate limiting"
    )