import argparse
from ui import KindleHighlightsApp


def main():
    parser = argparse.ArgumentParser(description="Kindle Clippings Viewer")
    parser.add_argument(
        "--file",
        type=str,
        default="My Clippings.txt",
        help="Path to My Clippings.txt file",
    )
    args = parser.parse_args()
    app = KindleHighlightsApp(args.file)
    app.run()


if __name__ == "__main__":
    main()
