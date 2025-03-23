from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import (
    Header,
    Footer,
    ListView,
    ListItem,
    Label,
    Markdown,
)

from clipping_processor import get_books_titles, get_book_highlights


class HighlightViewer(Markdown):
    """Widget to display highlights from a selected book."""

    book_title = reactive("")
    highlights = reactive([])

    def on_mount(self) -> None:
        self.styles.height = "100%"
        self.update_content()

    def watch_book_title(self) -> None:
        if self.book_title:
            self.highlights = get_book_highlights(
                self.app.clippings_file, self.book_title
            )
            self.update_content()

    def update_content(self) -> None:
        if not self.book_title:
            self.update("Select a book to view highlights")
            return

        if not self.highlights:
            self.update(f"No highlights found for {self.book_title}")
            return

        content = [f"# {self.book_title}\n"]

        for highlight in self.highlights:
            content.append(f"> {highlight['text']}")
            content.append(f"\n— {highlight['location']} - {highlight['date']}*\n")
            content.append("---")

        self.update("\n".join(content))


class BookList(ListView):
    """List view of available books"""

    def on_mount(self) -> None:
        self.styles.width = "30%"
        self.styles.height = "100%"
        self.load_books()

    def load_books(self) -> None:
        books = get_books_titles(self.app.clippings_file)
        for book in books:
            self.append(ListItem(Label(book)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        book_title = event.item.children[0].renderable
        self.app.query_one(HighlightViewer).book_title = book_title


class KindleHighlightsApp(App):
    CSS = """
    HighlightViewer {
        /* margin: 1; */
        /* padding: 1; */
        background: $surface;
        border: solid $primary;
        width: 1fr;
    }

    BookList {
        border: solid $primary;
    }

    #content {
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, clippings_file="My Clippings.txt"):
        self.clippings_file = clippings_file
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="content"):
            yield BookList()
            yield HighlightViewer()

        yield Footer()

    def on_mount(self) -> None:
        self.title = "Kindle Highlights"
        self.sub_title = "v0.1"

    def action_refresh(self) -> None:
        """Refresh the book list."""
        book_list = self.query_one(BookList)
        book_list.clear()
        book_list.load_books()


def run_app(clippings):
    """Run the Textual app with the provided clippings."""
    app = KindleHighlightsApp(clippings)
    app.run()
