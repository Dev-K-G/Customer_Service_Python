from prometheus_client import Counter, Histogram

class Metrics:
    # Counts how many times rate limits are exceeded
    RATE_LIMIT_HITS = Counter(
        "rate_limit_exceeded_total",
        "Total number of requests blocked by rate limiting"
    )


    # Counters
    KYC_UPDATE_COUNTER = Counter(
        "kyc_update_total",
        "Total number of KYC updates"
    )

    KYC_UPDATE_FAILURE_COUNTER = Counter(
        "kyc_update_failure_total",
        "Total failed KYC updates"
    )

    NOTIFICATION_CALL_COUNTER = Counter(
        "notification_calls_total",
        "Total calls to notification service"
    )

    NOTIFICATION_FAILURE_COUNTER = Counter(
        "notification_failure_total",
        "Failed notification calls"
    )

    # Latency tracking
    NOTIFICATION_LATENCY = Histogram(
        "notification_latency_seconds",
        "Notification service latency"
    )