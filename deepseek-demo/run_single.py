import argparse
from research_runner import run_research


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    args = parser.parse_args()
    query = args.query

    run_research(query)

if __name__ == "__main__":
    main()
