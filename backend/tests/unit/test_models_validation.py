"""Unit tests for model validation and edge cases.

These tests document the current validation behavior of models,
including edge cases that are NOT currently validated.
"""

import pytest
from pydantic import ValidationError

from app.models.item import ItemCreate, ItemUpdate
from app.models.learner import LearnerCreate
from app.models.interaction import InteractionLogCreate


class TestItemCreateEdgeCases:
    """Tests for ItemCreate schema edge cases."""

    def test_title_empty_string_is_accepted(self) -> None:
        """Empty title is currently accepted (no validation)."""
        item = ItemCreate(title="")
        assert item.title == ""

    def test_title_whitespace_only_is_accepted(self) -> None:
        """Title with only whitespace is currently accepted."""
        item = ItemCreate(title="   ")
        assert item.title == "   "

    def test_title_with_special_characters_valid(self) -> None:
        """Title with special characters should be valid."""
        item = ItemCreate(title="Test <>&\"' Item!")
        assert item.title == "Test <>&\"' Item!"

    def test_title_with_unicode_valid(self) -> None:
        """Title with unicode characters should be valid."""
        item = ItemCreate(title="Тест 测试 テスト 🔧")
        assert item.title == "Тест 测试 テスト 🔧"

    def test_parent_id_zero_is_accepted(self) -> None:
        """parent_id=0 is accepted (may cause issues with FK)."""
        item = ItemCreate(title="Child", parent_id=0)
        assert item.parent_id == 0

    def test_parent_id_negative_is_accepted(self) -> None:
        """Negative parent_id is currently accepted (no validation)."""
        item = ItemCreate(title="Child", parent_id=-1)
        assert item.parent_id == -1

    def test_description_default_is_empty_dict(self) -> None:
        """Description defaults to empty string."""
        item = ItemCreate(title="Test")
        assert item.description == ""


class TestItemUpdateEdgeCases:
    """Tests for ItemUpdate schema edge cases."""

    def test_update_title_empty_string_is_accepted(self) -> None:
        """Empty title in update is currently accepted."""
        update = ItemUpdate(title="", description="New desc")
        assert update.title == ""

    def test_update_description_empty_string_valid(self) -> None:
        """Empty description in update should be valid."""
        update = ItemUpdate(title="New Title", description="")
        assert update.description == ""


class TestLearnerCreateEdgeCases:
    """Tests for LearnerCreate schema edge cases."""

    def test_name_empty_string_is_accepted(self) -> None:
        """Empty name is currently accepted (no validation)."""
        learner = LearnerCreate(name="", email="test@example.com")
        assert learner.name == ""

    def test_email_empty_string_is_accepted(self) -> None:
        """Empty email is currently accepted (no validation)."""
        learner = LearnerCreate(name="Test User", email="")
        assert learner.email == ""

    def test_email_invalid_format_is_accepted(self) -> None:
        """Invalid email format is currently accepted (no validation)."""
        learner = LearnerCreate(name="Test User", email="invalid-email")
        assert learner.email == "invalid-email"

    def test_email_with_plus_valid(self) -> None:
        """Email with plus sign should be valid."""
        learner = LearnerCreate(name="Test", email="user+tag@example.com")
        assert learner.email == "user+tag@example.com"

    def test_name_with_unicode_valid(self) -> None:
        """Name with unicode characters should be valid."""
        learner = LearnerCreate(name="Іван Петренко", email="ivan@example.com")
        assert learner.name == "Іван Петренко"

    def test_email_with_subdomain_valid(self) -> None:
        """Email with subdomain should be valid."""
        learner = LearnerCreate(name="Test", email="user@mail.sub.example.com")
        assert learner.email == "user@mail.sub.example.com"


class TestInteractionLogCreateEdgeCases:
    """Tests for InteractionLogCreate schema edge cases."""

    def test_kind_empty_string_is_accepted(self) -> None:
        """Empty kind is currently accepted (no validation)."""
        interaction = InteractionLogCreate(learner_id=1, item_id=1, kind="")
        assert interaction.kind == ""

    def test_learner_id_zero_is_accepted(self) -> None:
        """learner_id=0 is currently accepted (FK validated at DB level)."""
        interaction = InteractionLogCreate(learner_id=0, item_id=1, kind="attempt")
        assert interaction.learner_id == 0

    def test_item_id_zero_is_accepted(self) -> None:
        """item_id=0 is currently accepted (FK validated at DB level)."""
        interaction = InteractionLogCreate(learner_id=1, item_id=0, kind="attempt")
        assert interaction.item_id == 0

    def test_learner_id_negative_is_accepted(self) -> None:
        """Negative learner_id is currently accepted (no validation)."""
        interaction = InteractionLogCreate(learner_id=-1, item_id=1, kind="attempt")
        assert interaction.learner_id == -1

    def test_item_id_negative_is_accepted(self) -> None:
        """Negative item_id is currently accepted (no validation)."""
        interaction = InteractionLogCreate(learner_id=1, item_id=-1, kind="attempt")
        assert interaction.item_id == -1

    def test_kind_with_spaces_valid(self) -> None:
        """Kind with spaces should be valid."""
        interaction = InteractionLogCreate(
            learner_id=1, item_id=1, kind="view attempt"
        )
        assert interaction.kind == "view attempt"

    def test_kind_with_special_characters_valid(self) -> None:
        """Kind with special characters should be valid."""
        interaction = InteractionLogCreate(
            learner_id=1, item_id=1, kind="attempt<1>"
        )
        assert interaction.kind == "attempt<1>"


class TestLargeInputEdgeCases:
    """Tests for large input values (boundary testing)."""

    def test_very_long_title_accepted(self) -> None:
        """Very long titles (1000+ chars) are currently accepted."""
        long_title = "A" * 1000
        item = ItemCreate(title=long_title)
        assert len(item.title) == 1000

    def test_very_long_description_accepted(self) -> None:
        """Very long descriptions are currently accepted."""
        long_desc = "B" * 5000
        item = ItemCreate(title="Test", description=long_desc)
        assert len(item.description) == 5000

    def test_very_long_name_accepted(self) -> None:
        """Very long names are currently accepted."""
        long_name = "C" * 500
        learner = LearnerCreate(name=long_name, email="test@example.com")
        assert len(learner.name) == 500

    def test_large_learner_id_accepted(self) -> None:
        """Large learner_id values are accepted."""
        interaction = InteractionLogCreate(
            learner_id=2**31 - 1, item_id=1, kind="attempt"
        )
        assert interaction.learner_id == 2**31 - 1

    def test_large_item_id_accepted(self) -> None:
        """Large item_id values are accepted."""
        interaction = InteractionLogCreate(
            learner_id=1, item_id=2**31 - 1, kind="attempt"
        )
        assert interaction.item_id == 2**31 - 1
