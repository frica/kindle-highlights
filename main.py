import argparse
import os


def get_book_highlights(file_path, title_name):
    """get book highlights for a given book"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Manually remove any stray BOM characters throughout the file
    content = content.replace("\ufeff", "")

    clippings = content.split("==========")

    list_highlight = []

    for i, clipping in enumerate(clippings):
        clipping = clipping.strip()
        if not clipping:
            continue

        # Extract the book title and highlight
        lines = clipping.split("\n")

        title = lines[0].strip()

        if title == title_name:
            if len(lines) < 3:
                print(f"Skipping clipping {i + 1}: not enough lines")
                continue

            highlight = lines[
                -1
            ].strip()  # The last non-empty line should be the highlight
            list_highlight.append(highlight)

    return list_highlight


def get_books_titles(file_path):
    """get book titles"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Manually remove any stray BOM characters throughout the file
    content = content.replace("\ufeff", "")

    clippings = content.split("==========")

    books = []

    for i, clipping in enumerate(clippings):
        clipping = clipping.strip()
        if not clipping:
            continue

        # Extract the book title and highlight
        lines = clipping.split("\n")

        title = lines[0].strip()

        if title not in books:
            books.append(title)

    return books


def scan(file, arguments):
    """scan the MyClippings file and process it given the CL arguments"""
    file_path = file
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    if arguments.find:
        highlights = get_book_highlights(file, arguments.find)
        if len(highlights):
            print(f"# {arguments.find}\n")
            for h in highlights:
                print(f"> {h}\n")
        else:
            print(f"Highlights for book {arguments.find} not found.")

    books_titles = get_books_titles(file_path)

    if arguments.list:
        for title in books_titles:
            print(f"* {title}")

    if arguments.count:
        print(f"Number of books: {len(books_titles)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="kindle-highlights",
        description="The application gives various information about the clippings file of your Kindle",
        epilog="Example: python main.py 'My-Clippings.txt' -f 'Vision Aveugle (Peter Watts)'",
    )

    parser.add_argument("filename")  # the MyClippings.txt file to look at
    parser.add_argument(
        "-l", "--list", action="store_true"
    )  # list all available books with notes
    parser.add_argument("-c", "--count", action="store_true")  # switch to get a count
    parser.add_argument("-f", "--find")

    args = parser.parse_args()
    scan(args.filename, args)
