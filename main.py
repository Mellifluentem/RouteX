
from checks.ping import check_ping
from checks.http import check_http


def main():
    print("\n================================")
    print("    MONITORING PLATFORM V0.2")
    print("================================")
    print("1. Ping")
    print("2. HTTP / HTTPS")

    choice = input("Select monitor type (1/2): ").strip()

    if choice == "1":
        target = input("Enter an IP address or hostname: ").strip()
        result = check_ping(target)

    elif choice == "2":
        target = input("Enter an HTTP/HTTPS URL: ").strip()
        result = check_http(target)

    else:
        print("Invalid choice. Please select 1 or 2.")
        return

    print("\n---------- Result ----------")
    print(f"Target: {target}")
    print(f"Status: {result['status']}")

    if result["latency_ms"] is not None:
        print(f"Latency: {result['latency_ms']} ms")

    if result.get("http_status_code") is not None:
        print(f"HTTP Status Code: {result['http_status_code']}")

    if result["error"]:
        print(f"Reason: {result['error']}")


if __name__ == "__main__":
    main()
