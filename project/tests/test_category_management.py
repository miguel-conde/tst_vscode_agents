"""Tests for category management functionality."""

import pytest
from pathlib import Path
import json
from src.timer import get_valid_categories, add_category, remove_category, reset_categories, VALID_CATEGORIES


class TestGetValidCategories:
    """Tests for getting valid categories."""

    def test_get_valid_categories_returns_default(self):
        """Test that default categories are returned initially."""
        categories = get_valid_categories()

        assert isinstance(categories, list)
        assert "feature" in categories
        assert "bug" in categories
        assert "refactor" in categories
        assert "docs" in categories
        assert "meeting" in categories

    def test_get_valid_categories_includes_defaults(self):
        """Test that all default categories are included."""
        categories = get_valid_categories()

        for category in VALID_CATEGORIES:
            assert category in categories


class TestAddCategory:
    """Tests for adding custom categories."""

    @pytest.fixture(autouse=True)
    def reset_after_test(self):
        """Reset categories before and after each test."""
        reset_categories()  # Reset before test
        yield
        reset_categories()  # Reset after test

    def test_add_category_successfully(self):
        """Test adding a new category."""
        result = add_category("testing")

        assert result is True
        categories = get_valid_categories()
        assert "testing" in categories

    def test_add_multiple_categories(self):
        """Test adding multiple custom categories."""
        add_category("testing")
        add_category("deployment")
        add_category("review")

        categories = get_valid_categories()
        assert "testing" in categories
        assert "deployment" in categories
        assert "review" in categories

    def test_add_duplicate_category_returns_false(self):
        """Test that adding duplicate category returns False."""
        add_category("testing")
        result = add_category("testing")

        assert result is False

    def test_add_existing_default_category_returns_false(self):
        """Test that adding existing default category returns False."""
        result = add_category("feature")

        assert result is False

    def test_add_category_with_spaces(self):
        """Test adding category with spaces."""
        result = add_category("code review")

        assert result is True
        assert "code review" in get_valid_categories()

    def test_add_category_case_sensitive(self):
        """Test that categories are case-sensitive."""
        add_category("Testing")
        add_category("testing")

        categories = get_valid_categories()
        assert "Testing" in categories
        assert "testing" in categories

    def test_add_empty_category_raises_error(self):
        """Test that adding empty category raises ValueError."""
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            add_category("")

    def test_add_whitespace_only_category_raises_error(self):
        """Test that whitespace-only category raises ValueError."""
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            add_category("   ")

    def test_add_none_category_raises_error(self):
        """Test that None category raises ValueError."""
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            add_category(None)

    def test_added_categories_persist_across_calls(self):
        """Test that added categories persist."""
        add_category("testing")

        # Call get_valid_categories multiple times
        categories1 = get_valid_categories()
        categories2 = get_valid_categories()

        assert "testing" in categories1
        assert "testing" in categories2


class TestRemoveCategory:
    """Tests for removing categories."""

    @pytest.fixture(autouse=True)
    def reset_after_test(self):
        """Reset categories before and after each test."""
        reset_categories()  # Reset before test
        yield
        reset_categories()  # Reset after test

    def test_remove_custom_category(self):
        """Test removing a custom category."""
        add_category("testing")
        result = remove_category("testing")

        assert result is True
        assert "testing" not in get_valid_categories()

    def test_remove_nonexistent_category_returns_false(self):
        """Test that removing nonexistent category returns False."""
        result = remove_category("nonexistent")

        assert result is False

    def test_cannot_remove_default_category(self):
        """Test that default categories cannot be removed."""
        result = remove_category("feature")

        assert result is False
        assert "feature" in get_valid_categories()

    def test_remove_multiple_custom_categories(self):
        """Test removing multiple custom categories."""
        add_category("testing")
        add_category("deployment")

        remove_category("testing")
        remove_category("deployment")

        categories = get_valid_categories()
        assert "testing" not in categories
        assert "deployment" not in categories

    def test_remove_category_case_sensitive(self):
        """Test that category removal is case-sensitive."""
        add_category("Testing")

        result = remove_category("testing")  # lowercase

        assert result is False
        assert "Testing" in get_valid_categories()


class TestResetCategories:
    """Tests for resetting categories to defaults."""

    def test_reset_categories_removes_custom(self):
        """Test that reset removes all custom categories."""
        add_category("testing")
        add_category("deployment")

        reset_categories()

        categories = get_valid_categories()
        assert "testing" not in categories
        assert "deployment" not in categories

    def test_reset_categories_keeps_defaults(self):
        """Test that reset keeps all default categories."""
        add_category("testing")

        reset_categories()

        categories = get_valid_categories()
        for category in VALID_CATEGORIES:
            assert category in categories

    def test_reset_categories_multiple_times(self):
        """Test that reset can be called multiple times."""
        add_category("testing")
        reset_categories()
        reset_categories()

        categories = get_valid_categories()
        assert len(categories) == len(VALID_CATEGORIES)


class TestCategoryPersistence:
    """Tests for category persistence across sessions."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Use temporary storage for tests."""
        monkeypatch.setattr("src.timer.get_categories_file", lambda: tmp_path / "categories.json")
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_after_test(self, temp_storage_dir):
        """Reset categories after each test."""
        yield
        reset_categories()

    def test_categories_saved_to_file(self, temp_storage_dir):
        """Test that custom categories are saved to file."""
        add_category("testing")

        categories_file = temp_storage_dir / "categories.json"
        assert categories_file.exists()

        with open(categories_file, "r") as f:
            data = json.load(f)

        assert "custom_categories" in data
        assert "testing" in data["custom_categories"]

    def test_categories_loaded_from_file(self, temp_storage_dir):
        """Test that categories are loaded from file."""
        # Save custom categories
        add_category("testing")
        add_category("deployment")

        # Simulate restart by clearing the cache and forcing reload
        import src.timer as timer_module

        timer_module._custom_categories_cache = None

        # Categories should be loaded from file
        categories = get_valid_categories()
        assert "testing" in categories
        assert "deployment" in categories
