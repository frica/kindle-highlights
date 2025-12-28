from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from textual.widgets import (
    Header,
    Footer,
    ListView,
    ListItem,
    Label,
    Markdown,
    Input,
)
from textual.containers import Vertical  # Changed VGroup to Vertical

from clipping_processor import get_books_titles, get_book_highlights


class BookSearch(Input):
    """Search box with custom Tab focus behavior."""

    BINDINGS = [
        Binding("tab", "focus_list", show=False, priority=True),
    ]

    def action_focus_list(self) -> None:
        self.app.query_one("#book_list_view", ListView).focus()


class BookListView(ListView):
    """Book list with custom Tab focus behavior."""

    BINDINGS = [
        Binding("tab", "focus_highlights", show=False, priority=True),
    ]

    def action_focus_highlights(self) -> None:
        self.app.query_one("#highlight_viewer", HighlightViewer).focus()


class HighlightViewer(Markdown):
    """Widget to display highlights from a selected book."""

    BINDINGS = [
        Binding("tab", "focus_search", show=False, priority=True),
        Binding("down", "scroll_down", show=False, priority=True),
        Binding("up", "scroll_up", show=False, priority=True),
    ]

    book_title = reactive("")
    highlights = reactive([])
    can_focus = True

    def action_focus_search(self) -> None:
        self.app.query_one("#book_search", Input).focus()

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

        content = [f"# {self.book_title}"]
        if self.highlights:
            author = self.highlights[0]["author"]
            content.append(f"# ({author})\n")
            content.append("---")

        for highlight in self.highlights:
            content.append(f"> {highlight['text']}")
            content.append(f"\n— {highlight['location']} - _{highlight['date']}_\n")
            content.append("---")

        self.update("\n".join(content))


class BookList(Vertical): # Changed VGroup to Vertical
    """Book list with search functionality."""

    DEFAULT_CSS = """
    BookList {
        width: 30%;
        height: 100%;
    }
    #book_search {
        border: round $primary;
        margin-bottom: 0;
    }
    #book_list_view {
        height: 1fr;
        border: round $primary;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._original_books = []

    def compose(self) -> ComposeResult:
        yield BookSearch(placeholder="Search books", id="book_search")
        yield BookListView(id="book_list_view")

    def on_mount(self) -> None:
        self.load_books()

    def load_books(self) -> None:
        self._original_books = get_books_titles(self.app.clippings_file)
        book_list_view = self.query_one("#book_list_view", ListView)
        book_list_view.clear()
        for book_title in self._original_books:
            book_list_view.append(ListItem(Label(book_title)))

    async def on_input_changed(self, event: Input.Changed) -> None:
        search_term = event.value.lower()
        book_list_view = self.query_one("#book_list_view", ListView)
        book_list_view.clear()

        if not search_term:
            for book_title in self._original_books:
                book_list_view.append(ListItem(Label(book_title)))
        else:
            filtered_books = [
                book for book in self._original_books if search_term in book.lower()
            ]
            for book_title in filtered_books:
                book_list_view.append(ListItem(Label(book_title)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        # Ensure we are reacting to selections from the correct ListView
        if event.list_view.id == "book_list_view":
            book_title = event.item.children[0].content
            highlight_viewer = self.app.query_one("#highlight_viewer", HighlightViewer)
            highlight_viewer.book_title = str(book_title)


class KindleHighlightsApp(App):
    CSS = """
    HighlightViewer {
        /* margin: 1; */
        /* padding: 1; */
        background: $surface;
        border: solid $primary;
        width: 1fr;
        overflow-y: auto;
        scrollbar-size: 1 1;
    }

    /*BookList {
        border: solid $primary;
    }*/ /* Removed as BookList is now a VGroup */

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
            yield HighlightViewer(id="highlight_viewer")

        yield Footer()

    def on_mount(self) -> None:
        self.title = "Kindle Highlights"
        self.sub_title = "v0.2"

    def action_refresh(self) -> None:
        """Refresh the book list."""
        book_list_widget = self.query_one(BookList)
        # The load_books method now handles clearing and loading into the ListView child
        book_list_widget.load_books()
        # Clear the search input as well
        search_input = book_list_widget.query_one("#book_search", Input)
        search_input.value = ""


def run_app(clippings):
    """Run the Textual app with the provided clippings."""
    app = KindleHighlightsApp(clippings)
    app.run()
