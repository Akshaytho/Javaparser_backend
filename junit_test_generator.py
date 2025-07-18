"""Helpers to ask a language model for JUnit tests."""

from __future__ import annotations



import logging
import os

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
os.environ.setdefault("LANGCHAIN_API_KEY", "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")
os.environ.setdefault("LANGCHAIN_PROJECT", "JUnit_test_generation")

try:
    from langchain.chat_models import ChatOpenAI
except Exception:  # pragma: no cover - langchain may not be installed in tests
    ChatOpenAI = None

try:  # pragma: no cover - langsmith is optional in tests
    from langsmith import traceable
except Exception:  # pragma: no cover - langsmith may not be installed
    def traceable(_func=None, **_kwargs):
        """Fallback no-op decorator when ``langsmith`` is missing."""

        def decorator(func):
            return func

        if _func is None:
            return decorator
        return decorator(_func)


logger = logging.getLogger(__name__)


def _craft_prompt(method_code: str) -> str:
    """Create the English instructions sent to the model."""

    return (
        "You are a senior Java developer. "
        "Write a JUnit 5 test for the following Java method. "
        "Include parameterized tests and Mockito when helpful.\n\n" + method_code
    )


def _call_llm(prompt: str) -> str:
    """Return the model's reply for ``prompt`` or an empty string."""

    if ChatOpenAI is not None:
        logger.info("Requesting completion from LLM")
        llm = ChatOpenAI(model_name="gpt-4o", max_tokens=800)
        result = llm.invoke(prompt)
        return result.content.strip()

    # No language model available
    return ""


@traceable
def generate_junit_test(java_method_code: str) -> str:
    """Return the JUnit test generated for ``java_method_code``."""

    logger.info("Generating JUnit test")
    prompt = _craft_prompt(java_method_code)
    return _call_llm(prompt)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from extract_method import extract_method

    method_code = extract_method("HelloWorld.java")
    print("Extracted Method:\n", method_code)
    junit_test = generate_junit_test(method_code)
    print("\nGenerated JUnit Test:\n", junit_test)
