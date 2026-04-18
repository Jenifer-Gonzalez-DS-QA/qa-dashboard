"""
test_runner.py
Ejecuta pruebas de API contra JSONPlaceholder y guarda resultados en CSV.
https://jsonplaceholder.typicode.com — Sin registro, sin API key, gratuito 24/7.
"""

import requests
import csv
import time
import os
from datetime import datetime

BASE_URL = "https://jsonplaceholder.typicode.com"
RESULTS_FILE = "data/test_results.csv"
os.makedirs("data", exist_ok=True)

# (nombre, método, endpoint, payload, status_esperado)

TESTS = [
    # ── POSTS ────────────────────────────────────────────────────────────────
    ("GET posts - listado completo",     "GET",    "/posts",
     None,                                              200),
    ("GET posts - filtrar por userId",   "GET",    "/posts",
     None,                                              200),
    ("GET post por ID",                  "GET",    "/posts/1",
     None,                                              200),
    ("GET post no existe",               "GET",    "/posts/9999",
     None,                                              404),
    ("POST crear post",                  "POST",   "/posts",
     {"title": "QA Post", "body": "Test", "userId": 1}, 201),
    ("PUT actualizar post completo",     "PUT",    "/posts/1",
     {"id": 1, "title": "Updated", "body": "B", "userId": 1}, 200),
    ("PATCH actualizar post parcial",    "PATCH",  "/posts/1",
     {"title": "Patched Title"},                        200),
    ("DELETE eliminar post",             "DELETE", "/posts/1",
     None,                                              200),
    # ── USUARIOS ─────────────────────────────────────────────────────────────
    ("GET usuarios - listado",           "GET",    "/users",
     None,                                              200),
    ("GET usuario por ID",               "GET",    "/users/1",
     None,                                              200),
    ("GET usuario no existe",            "GET",    "/users/9999",
     None,                                              404),
    ("POST crear usuario",               "POST",   "/users",
     {"name": "Jenifer", "email": "j@qa.com"},          201),
    ("PUT actualizar usuario",           "PUT",    "/users/1",
     {"name": "Jenifer U", "email": "j@qa.com"},        200),
    ("DELETE eliminar usuario",          "DELETE", "/users/1",
     None,                                              200),
    # ── COMENTARIOS ──────────────────────────────────────────────────────────
    ("GET comentarios - listado",        "GET",    "/comments",
     None,                                              200),
    ("GET comentarios por postId",       "GET",    "/comments",
     None,                                              200),
    ("GET comentario por ID",            "GET",    "/comments/1",
     None,                                              200),
    ("GET comentario no existe",         "GET",    "/comments/9999",
     None,                                              404),
    ("POST crear comentario",            "POST",   "/comments",
     {"postId": 1, "name": "QA", "email": "j@qa.com", "body": "Test"}, 201),
    # ── TODOS ─────────────────────────────────────────────────────────────────
    ("GET todos - listado",              "GET",    "/todos",
     None,                                              200),
    ("GET todo por ID",                  "GET",    "/todos/1",
     None,                                              200),
    ("GET todo no existe",               "GET",    "/todos/9999",
     None,                                              404),
]


def run_test(name, method, endpoint, payload, expected_status):
    url = f"{BASE_URL}{endpoint}"
    start = time.time()
    try:
        params = None
        # Casos con params en GET
        if endpoint == "/posts" and name == "GET posts - filtrar por userId":
            params = {"userId": 1}
        if endpoint == "/comments" and name == "GET comentarios por postId":
            params = {"postId": 1}
        if method == "GET":
            r = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            r = requests.post(url, json=payload, timeout=10)
        elif method == "PUT":
            r = requests.put(url, json=payload, timeout=10)
        elif method == "PATCH":
            r = requests.patch(url, json=payload, timeout=10)
        elif method == "DELETE":
            r = requests.delete(url, timeout=10)

        elapsed = round((time.time() - start) * 1000, 2)
        passed = r.status_code == expected_status
        return {
            "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_name":        name,
            "method":           method,
            "endpoint":         endpoint,
            "expected_status":  expected_status,
            "actual_status":    r.status_code,
            "passed":           passed,
            "response_time_ms": elapsed,
            "error":            ""
        }
    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 2)
        return {
            "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_name":        name,
            "method":           method,
            "endpoint":         endpoint,
            "expected_status":  expected_status,
            "actual_status":    "ERROR",
            "passed":           False,
            "response_time_ms": elapsed,
            "error":            str(e)
        }


def main():
    print(f"\n{'='*65}")
    print(f"  QA Dashboard — Test Runner")
    print(f"  API: {BASE_URL}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*65}\n")

    results = []
    for name, method, endpoint, payload, expected in TESTS:
        result = run_test(name, method, endpoint, payload, expected)
        results.append(result)
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(
            f"{status} | {method:<6} | {result['actual_status']} | {result['response_time_ms']:>7} ms | {name}")

    fieldnames = ["timestamp", "test_name", "method", "endpoint",
                  "expected_status", "actual_status", "passed", "response_time_ms", "error"]
    write_header = not os.path.exists(RESULTS_FILE)
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(results)

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\n{'='*65}")
    print(
        f"  Total: {total} | ✅ Pasaron: {passed} | ❌ Fallaron: {total - passed}")
    print(f"  Resultados guardados en: {RESULTS_FILE}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
