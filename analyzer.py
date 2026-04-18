"""
analyzer.py
Carga los resultados del CSV y genera métricas de calidad con pandas.
"""

import pandas as pd
import os


def load_results(filepath="data/test_results.csv"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"No se encontró '{filepath}'.\n"
            "Ejecuta primero: python test_runner.py"
        )
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["passed"] = df["passed"].astype(bool)
    return df


def general_metrics(df):
    total = len(df)
    passed = df["passed"].sum()
    failed = total - passed
    return {
        "total_tests":   total,
        "passed":        int(passed),
        "failed":        int(failed),
        "pass_rate_pct": round((passed / total) * 100, 2) if total > 0 else 0,
        "avg_time_ms":   round(df["response_time_ms"].mean(), 2),
        "max_time_ms":   round(df["response_time_ms"].max(), 2),
        "min_time_ms":   round(df["response_time_ms"].min(), 2),
    }


def metrics_by_method(df):
    grouped = df.groupby("method").agg(
        total=("passed", "count"),
        passed=("passed", "sum"),
        avg_time_ms=("response_time_ms", "mean"),
    ).reset_index()
    grouped["pass_rate_pct"] = (
        grouped["passed"] / grouped["total"] * 100).round(2)
    grouped["avg_time_ms"] = grouped["avg_time_ms"].round(2)
    return grouped.sort_values("total", ascending=False)


def slowest_tests(df, n=5):
    return (
        df[["test_name", "method", "response_time_ms", "passed"]]
        .sort_values("response_time_ms", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def failed_tests(df):
    return df[~df["passed"]][
        ["test_name", "method", "endpoint",
         "expected_status", "actual_status", "response_time_ms", "error"]
    ].reset_index(drop=True)


def trend_over_time(df):
    df = df.copy()
    df["run"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    trend = df.groupby("run").agg(
        total=("passed", "count"),
        passed=("passed", "sum"),
        avg_time_ms=("response_time_ms", "mean"),
    ).reset_index()
    trend["pass_rate_pct"] = (trend["passed"] / trend["total"] * 100).round(2)
    trend["avg_time_ms"] = trend["avg_time_ms"].round(2)
    return trend


def print_summary(df):
    m = general_metrics(df)
    print(f"\n{'='*55}")
    print(f"  📊 RESUMEN GENERAL DE CALIDAD")
    print(f"{'='*55}")
    print(f"  Total pruebas   : {m['total_tests']}")
    print(f"  ✅ Pasaron      : {m['passed']}")
    print(f"  ❌ Fallaron     : {m['failed']}")
    print(f"  📈 Tasa éxito   : {m['pass_rate_pct']}%")
    print(f"  ⏱  Prom.        : {m['avg_time_ms']} ms")
    print(f"  🐢 Máximo       : {m['max_time_ms']} ms")
    print(f"  🚀 Mínimo       : {m['min_time_ms']} ms")
    print(f"\n{'-'*55}")
    print(f"  POR MÉTODO HTTP")
    print(f"{'-'*55}")
    print(metrics_by_method(df).to_string(index=False))
    failed = failed_tests(df)
    if not failed.empty:
        print(f"\n{'-'*55}")
        print(f"  ⚠️  FALLIDAS")
        print(f"{'-'*55}")
        print(failed.to_string(index=False))
    print(f"{'='*55}\n")


if __name__ == "__main__":
    df = load_results()
    print_summary(df)
