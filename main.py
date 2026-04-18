from test_runner import main as run_tests
from analyzer import load_results, print_summary
from dashboard import build_dashboard


def main():
    print("\n🚀 Iniciando flujo QA Dashboard…\n")
    run_tests()
    df = load_results()
    print_summary(df)
    output = build_dashboard(df)
    print(f"\n🎉 Listo. Abre en tu navegador:\n   {output}\n")


if __name__ == "__main__":
    main()
