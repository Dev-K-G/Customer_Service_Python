from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'request_count',
    'Total API Requests'
)

ERROR_COUNT = Counter(
    'error_count',
    'Total Errors'
)

LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency'
)

transactions_total = Counter(
    'transactions_total',
    'Total transactions processed'
)

failed_transfers_total = Counter(
    'failed_transfers_total',
    'Failed operations'
)