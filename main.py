
from checks.ping import check_ping


def main():
    target = input("Enter an IP address or hostname: ").strip()

    result = check_ping(target)

    print("\n================================")
    print("    MONITORING PLATFORM V0.1")
    print("================================")
    print(f"Target: {target}")
    print(f"Status: {result['status']}")

    if result["latency_ms"] is not None:
        print(f"Latency: {result['latency_ms']} ms")

    if result["error"]:
        print(f"Reason: {result['error']}")


if __name__ == "__main__":
    main()
