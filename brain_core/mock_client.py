# brain_core/mock_client.py
"""
Mock OpenAI client for development.
Returns predictable responses without making API calls.
"""


class MockChatCompletion:
    """Mock chat completion response object."""

    def __init__(self, content: str):
        self.choices = [MockChoice(content)]


class MockChoice:
    """Mock choice object."""

    def __init__(self, content: str):
        self.message = MockMessage(content)


class MockMessage:
    """Mock message object."""

    def __init__(self, content: str):
        self.content = content


class MockCompletions:
    """Mock completions namespace."""

    def create(self, model: str, messages: list[dict], **kwargs) -> MockChatCompletion:
        """
        Generate a mock response based on the conversation.
        
        Returns a predictable response that:
        - Acknowledges the user's message
        - References the project if mentioned
        - Provides a generic helpful response
        """
        # Extract user message (usually the last message)
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        last_user_msg = user_messages[-1]["content"] if user_messages else ""

        # Extract system messages for context
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        project_context = ""
        for sys_msg in system_messages:
            content = sys_msg.get("content", "")
            if "project" in content.lower():
                project_context = content

        # Generate mock response
        response_parts = [
            "[MOCK MODE] This is a development response. No API call was made.",
            "",
            f"I understand you're asking about: {last_user_msg[:100]}...",
        ]

        if project_context:
            response_parts.append(
                "\nI have access to project context from the database."
            )

        response_parts.append(
            "\nIn production, I would provide a detailed response based on "
            "the conversation history and project knowledge stored in the database."
        )

        return MockChatCompletion("\n".join(response_parts))


class MockChat:
    """Mock chat namespace."""

    def __init__(self):
        self.completions = MockCompletions()


class MockOpenAIClient:
    """
    Mock OpenAI client that mimics the OpenAI API structure
    but returns predictable responses without making HTTP requests.
    """

    def __init__(self):
        self.chat = MockChat()

