import pytest
from unittest.mock import patch
import pytest_asyncio # Import pytest_asyncio

from textual.pilot import Pilot
from textual.widgets import ListView, ListItem, Label, Input

# Assuming your app is in 'main.py' or 'ui.py'
# If main.py also runs the app, we might need to be careful with imports
# For this example, let's assume KindleHighlightsApp and BookList are directly importable from ui
from ui import KindleHighlightsApp, BookList # Assuming BookList is directly part of ui.py

# Dummy book data for mocking
DUMMY_BOOKS = ["Apple Book", "Banana Thoughts", "Another Apple Story", "Orange World"]
DUMMY_HIGHLIGHTS = {
    "Apple Book": [{"text": "Highlight 1", "location": "p1", "date": "2023-01-01", "author": "Author A"}],
    "Banana Thoughts": [{"text": "Highlight 2", "location": "p2", "date": "2023-01-02", "author": "Author B"}],
    "Another Apple Story": [{"text": "Highlight 3", "location": "p3", "date": "2023-01-03", "author": "Author C"}],
    "Orange World": [{"text": "Highlight 4", "location": "p4", "date": "2023-01-04", "author": "Author D"}],
}

# Removed autouse=True fixture mock_clipping_processor

@pytest_asyncio.fixture
async def app_pilot():
    """Provides a Textual Pilot for the app with integrated mocking."""
    with patch("ui.get_books_titles", return_value=DUMMY_BOOKS) as mock_get_titles, \
         patch("ui.get_book_highlights", side_effect=lambda _, title: DUMMY_HIGHLIGHTS.get(title, [])) as mock_get_highlights:
        # Pass a dummy clippings_file as it's expected by __init__
        # The mocks should prevent actual file access for these functions.
        app = KindleHighlightsApp(clippings_file="dummy_clippings.txt")
        async with app.run_test() as pilot:
            yield pilot

class TestBookSearch:
    @pytest.mark.asyncio
    async def _get_book_list_items(self, pilot: Pilot) -> list[str]: # This helper is not a test, so it doesn't strictly need the marker, but it's an async function called by tests.
        """Helper to get current book titles from the ListView."""
        book_list_widget = pilot.app.query_one(BookList)
        list_view = book_list_widget.query_one("#book_list_view", ListView)
        return [item.query_one(Label).renderable for item in list_view.children if isinstance(item, ListItem)]

    @pytest.mark.asyncio
    async def test_initial_book_list_loaded(self, app_pilot: Pilot):
        """Test that the initial list of books is loaded correctly."""
        await app_pilot.pause() # Allow UI to settle
        book_titles = await self._get_book_list_items(app_pilot)
        assert sorted(book_titles) == sorted(DUMMY_BOOKS)
        assert len(book_titles) == len(DUMMY_BOOKS)

    @pytest.mark.asyncio
    async def test_search_input_exists(self, app_pilot: Pilot):
        """Test that the search input field exists."""
        await app_pilot.pause()
        book_list_widget = app_pilot.app.query_one(BookList)
        search_input = book_list_widget.query_one("#book_search", Input)
        assert search_input is not None
        assert search_input.placeholder == "Search books"

    @pytest.mark.asyncio
    async def test_search_filters_books_correctly(self, app_pilot: Pilot):
        """Test that typing in the search input filters the book list."""
        await app_pilot.pause()
        book_list_widget = app_pilot.app.query_one(BookList)
        search_input = book_list_widget.query_one("#book_search", Input)

        # Search for "Apple"
        search_input.value = "Apple" # Directly set value
        await app_pilot.pause() # Allow event propagation and UI update

        filtered_books = await self._get_book_list_items(app_pilot)
        expected_books = ["Apple Book", "Another Apple Story"]
        assert sorted(filtered_books) == sorted(expected_books)

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, app_pilot: Pilot):
        """Test that search is case-insensitive."""
        await app_pilot.pause()
        book_list_widget = app_pilot.app.query_one(BookList)
        search_input = book_list_widget.query_one("#book_search", Input)

        search_input.value = "apple" # Lowercase
        await app_pilot.pause()

        filtered_books = await self._get_book_list_items(app_pilot)
        expected_books = ["Apple Book", "Another Apple Story"]
        assert sorted(filtered_books) == sorted(expected_books)

    @pytest.mark.asyncio
    async def test_search_no_results(self, app_pilot: Pilot):
        """Test that an empty list is shown for a search term with no matches."""
        await app_pilot.pause()
        book_list_widget = app_pilot.app.query_one(BookList)
        search_input = book_list_widget.query_one("#book_search", Input)

        search_input.value = "NonExistentBook"
        await app_pilot.pause()

        filtered_books = await self._get_book_list_items(app_pilot)
        assert filtered_books == []

    @pytest.mark.asyncio
    async def test_search_empty_term_shows_all_books(self, app_pilot: Pilot):
        """Test that an empty search term shows all books."""
        await app_pilot.pause()
        book_list_widget = app_pilot.app.query_one(BookList)
        search_input = book_list_widget.query_one("#book_search", Input)

        # First, type something to filter
        search_input.value = "Apple"
        await app_pilot.pause()
        # Ensure it filtered
        assert len(await self._get_book_list_items(app_pilot)) == 2

        # Then, clear the input.
        search_input.value = ""
        await app_pilot.pause()

        filtered_books = await self._get_book_list_items(app_pilot)
        assert sorted(filtered_books) == sorted(DUMMY_BOOKS)

    @pytest.mark.asyncio
    async def test_refresh_action_clears_search_and_reloads(self, app_pilot: Pilot):
        """Test that the 'r' (refresh) action clears the search and reloads books."""
        await app_pilot.pause()
        book_list_widget = app_pilot.app.query_one(BookList)
        search_input = book_list_widget.query_one("#book_search", Input)

        # Type something in search
        search_input.value = "Banana"
        await app_pilot.pause()
        assert search_input.value == "Banana"
        filtered_books = await self._get_book_list_items(app_pilot)
        assert sorted(filtered_books) == ["Banana Thoughts"]

        # Press 'r' to refresh
        await app_pilot.app.action_refresh() # Directly call the action
        await app_pilot.pause() # Allow refresh action to complete

        # Check if search input is cleared
        assert search_input.value == ""

        # Check if book list is reloaded to original state
        reloaded_books = await self._get_book_list_items(app_pilot)
        assert sorted(reloaded_books) == sorted(DUMMY_BOOKS)

# To run these tests, you would typically use `pytest` in your terminal
# Ensure textual and pytest are installed.
# Example: pytest tests/test_ui.py
# You might need to create an empty __init__.py in the tests directory if it's treated as a package.
# Also, ensure your main application code (ui.py, clipping_processor.py) is in the PYTHONPATH.
# If you run pytest from the root of your project, it should generally work.
# For example, if your structure is:
# project_root/
#   ui.py
#   clipping_processor.py
#   tests/
#     test_ui.py
# Running `pytest` from `project_root` should find the tests and modules.
# If `clipping_processor` is not found, you might need to adjust PYTHONPATH or how you run pytest.
# One common way is to install your project in editable mode: `pip install -e .` (if you have a pyproject.toml/setup.py)
# Or add project root to PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:$(pwd)` before running pytest.
# For this specific environment, the tools will likely handle this.
# Consider adding an empty tests/__init__.py if pytest has module discovery issues.
# No, it is not needed for pytest.
# Let's also create an empty clipping_processor.py for the imports to work in this test environment
# if the real one is not accessible or for more isolated testing.
# However, the mock should prevent any actual code from clipping_processor from running.
# The `autouse=True` in the fixture means it will be used for all tests in this file.
# The `app_pilot` fixture also uses `app.run_test()` which is good for testing Textual apps.
# The `await app_pilot.type(search_input.id, "Apple")` might be problematic if search_input.id is None.
# Let's ensure #book_search is used as the selector for typing.
# The BookList widget itself is a VGroup, the Input is #book_search, and ListView is #book_list_view.
# So pilot.type should target the Input widget directly using its ID.
# The provided solution for clearing input by pressing backspace is a common workaround.
# Final check of the test logic:
# - Initial state: good.
# - Input exists: good.
# - Search filters: good.
# - Case insensitive: good.
# - No results: good.
# - Empty search term (clearing): good.
# - Refresh action: good.
# The helper `_get_book_list_items` is useful.
# The mocking setup seems correct.
# The use of `await app_pilot.pause()` is crucial for UI updates to reflect.
# The structure of the test class and its methods is standard for pytest.
# One minor adjustment: in `test_search_filters_books_correctly` and others,
# instead of `await app_pilot.type(search_input.id, "Apple")`,
# it's safer to use the known ID directly: `await app_pilot.type("#book_search", "Apple")`.
# This is because `search_input.id` might be `None` if not explicitly set in the `Input` widget's constructor.
# In `ui.py`, the Input is `yield Input(placeholder="Search books", id="book_search")`, so `id="book_search"` is set.
# So, `search_input.id` should be "book_search". This seems fine.
# Let's ensure the path to `ui.py` and `clipping_processor.py` is correct for the imports.
# The problem statement implies they are in the root.
# The test file is in `tests/test_ui.py`.
# Python's import system, when running `pytest` from the root, should handle this structure:
# `project_root/`
#   `ui.py`
#   `clipping_processor.py`
#   `tests/`
#     `test_ui.py`
# This is a standard layout.
# It might be beneficial to add `__init__.py` to the `tests` directory to ensure it's treated as a package,
# though pytest is often smart enough without it. I will omit it for now.
# The tests look comprehensive for the search functionality.
# The use of `sorted()` for list comparison is good practice when order doesn't matter.
# The `app.run_test()` context manager handles app startup and shutdown.
# The `autouse=True` for `mock_clipping_processor` means it will automatically apply to all test methods
# in `TestBookSearch`, which is what we want.
# The side_effect for `get_book_highlights` is a good way to return different highlights per book.
# The test for the refresh action also correctly checks that the search input is cleared.
# Looks good to go.
