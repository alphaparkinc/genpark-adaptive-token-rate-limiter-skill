import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from client import AdaptiveTokenRateLimiterClient

def main():
    client = AdaptiveTokenRateLimiterClient(max_tokens_per_min=5000)
    # Grant request 1
    p1 = client.acquire_token_permit(2000)
    print(f"Request 1: {p1['verdict']} (Remaining: {p1['remaining_tokens_budget']} tokens)")
    # Grant request 2
    p2 = client.acquire_token_permit(2500)
    print(f"Request 2: {p2['verdict']} (Remaining: {p2['remaining_tokens_budget']} tokens)")
    # Over capacity -> Backoff
    p3 = client.acquire_token_permit(2000)
    print(f"Request 3: {p3['verdict']} (Wait: {p3['wait_backoff_ms']}ms)")

if __name__ == '__main__':
    main()
