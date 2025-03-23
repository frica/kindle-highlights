import argparse
import os
from typing import Optional


def get_book_highlights(file_path, title_name):
    """Get book highlights for a given book with metadata"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Remove BOM characters
    content = content.replace("\ufeff", "")
    clippings = content.split("==========")

    highlights = []

    for clipping in clippings:
        clipping = clipping.strip()
        if not clipping:
            continue

        lines = clipping.split("\n")
        if len(lines) < 3:
            continue

        title = lines[0].strip()

        # Check if this clipping belongs to the requested book
        if title_name in title:
            # TODO: this should be better attached to the book rather than the highlight
            # extract the author name between the last parenthesis
            author = title.split("(")[-1].strip(")")
            metadata = lines[1].strip() if len(lines) > 1 else ""
            highlight_text = "\n".join(lines[2:]).strip()

            # Extract location and date if available
            location = ""
            date = ""
            # TODO: won't work with all languages, only french
            if "emplacement" in metadata:
                location_parts = metadata.split("emplacement")
                if len(location_parts) > 1:
                    location = "emplacement " + location_parts[1].split("|")[0].strip()
            # TODO: won't work with all languages, only french
            if "Ajouté le" in metadata:
                date_parts = metadata.split("Ajouté le")
                if len(date_parts) > 1:
                    date = "Ajouté le " + date_parts[1].strip()

            highlights.append(
                {
                    "title": title,
                    "author": author,
                    "text": highlight_text,
                    "location": location,
                    "date": date,
                    "metadata": metadata,
                }
            )

    return highlights


def get_books_titles(file_path):
    """Get book titles"""
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
        # keep the title only, strip what's after the first parenthesis' opening
        title = title.split("(")[0].strip()

        if title not in books:
            books.append(title)

    return books


def scan(file, arguments):
    """Scan the MyClippings file and process it given the CL arguments"""
    file_path = file
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # if arguments.find:
    #     highlights = get_book_highlights(file, arguments.find)
    #     if len(highlights):
    #         print(f"# {arguments.find}\n")
    #         for h in highlights:
    #             print(f"> {h}\n")
    #     else:
    #         print(f"Highlights for book {arguments.find} not found.")

    books_titles = get_books_titles(file_path)

    if arguments.list:
        for title in books_titles:
            print(f"* {title}")

    if arguments.count:
         print(f"Number of books: {len(books_titles)}")


def read_clippings_file(file_path: str) -> Optional[str]:
    """Read the My Clippings.txt file content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading clippings file: {e}")
        return None


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
