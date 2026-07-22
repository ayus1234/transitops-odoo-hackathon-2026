import time
import json
import urllib.request
import urllib.parse
import urllib.error
import statistics
import concurrent.futures

BASE_URL = "http://127.0.0.1:8000/api/v1"
ENDPOINTS = [
    "/dashboard/overview",
    "/vehicles?page=1&page_size=50",
    "/vehicles?search=ENT",
    "/trips?page=1&page_size=50",
    "/trips?status=Completed",
    "/maintenance?page=1&page_size=50",
    "/inventory/parts?page=1&page_size=50",
    "/activity?page=1&page_size=50"
]

NUM_REQUESTS_PER_ENDPOINT = 20
CONCURRENCY = 5

def get_auth_token():
    url = f"{BASE_URL}/auth/login"
    data = json.dumps({
        'email': 'admin@transitops.com',
        'password': 'admin123'
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data.get('access_token')
    except Exception as e:
        print(f"Failed to get auth token: {e}")
        return None

def make_request(endpoint, token):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Accept': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    start_time = time.time()
    status_code = 0
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response.read() # Read response body
    except urllib.error.HTTPError as e:
        status_code = e.code
    except Exception as e:
        status_code = 500
        print(f"Error requesting {endpoint}: {e}")
        
    duration = time.time() - start_time
    return (duration * 1000, status_code) # Return in ms

def run_benchmark():
    print("=====================================================")
    print("       API PERFORMANCE BENCHMARK - TRANSITOPS        ")
    print("=====================================================")
    
    token = get_auth_token()
    if not token:
        print("Could not obtain auth token. Aborting.")
        return
        
    print(f"Testing {len(ENDPOINTS)} endpoints...")
    print(f"Requests per endpoint: {NUM_REQUESTS_PER_ENDPOINT}")
    print(f"Concurrency level: {CONCURRENCY}")
    print("=====================================================\n")

    for endpoint in ENDPOINTS:
        print(f"Testing: {endpoint}")
        latencies = []
        successes = 0
        failures = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
            futures = [executor.submit(make_request, endpoint, token) for _ in range(NUM_REQUESTS_PER_ENDPOINT)]
            for future in concurrent.futures.as_completed(futures):
                latency, status_code = future.result()
                latencies.append(latency)
                if status_code == 200:
                    successes += 1
                else:
                    failures += 1
        
        latencies.sort()
        avg = statistics.mean(latencies)
        p50 = latencies[len(latencies)//2]
        p95 = latencies[int(len(latencies) * 0.95)] if len(latencies) > 0 else 0
        p99 = latencies[int(len(latencies) * 0.99)] if len(latencies) > 0 else 0
        
        print(f"  Result: {successes} Success, {failures} Failed")
        print(f"  Avg: {avg:.2f}ms | P50: {p50:.2f}ms | P95: {p95:.2f}ms | P99: {p99:.2f}ms")
        print("-" * 50)

if __name__ == "__main__":
    run_benchmark()
