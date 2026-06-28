from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT
from expenses_ai_agent.prompts.user import USER_PROMPT


class TestClassificationPrompt:
    """Tests for the system prompt."""

    def test_classification_prompt_exists(self):
        """CLASSIFICATION_PROMPT should be defined as a string constant."""
        assert isinstance(CLASSIFICATION_PROMPT, str)
        assert len(CLASSIFICATION_PROMPT) > 100

    def test_classification_prompt_contains_categories(self):
        """System prompt should mention all 12 expense categories."""
        required_categories = [
            "Food",
            "Transport",
            "Entertainment",
            "Shopping",
            "Health",
            "Bills",
            "Education",
            "Travel",
            "Services",
            "Gifts",
            "Investments",
            "Other",
        ]

        prompt_lower = CLASSIFICATION_PROMPT.lower()
        for category in required_categories:
            assert category.lower() in prompt_lower, f"Category '{category}' not found"

    def test_classification_prompt_mentions_json_output(self):
        """System prompt should mention JSON output format."""
        assert "json" in CLASSIFICATION_PROMPT.lower()


class TestUserPrompt:
    """Tests for the user prompt template."""

    def test_user_prompt_exists(self):
        """USER_PROMPT should be defined."""
        assert isinstance(USER_PROMPT, str)

    def test_user_prompt_has_placeholder(self):
        """USER_PROMPT should have a placeholder."""
        assert "{" in USER_PROMPT and "}" in USER_PROMPT

    def test_user_prompt_can_be_formatted(self):
        """USER_PROMPT should be formattable."""
        try:
            formatted = USER_PROMPT.format(expense_description="Coffee $5.50")
            assert "Coffee" in formatted or "5.50" in formatted
        except KeyError as e:
            assert "expense" in str(e).lower()
