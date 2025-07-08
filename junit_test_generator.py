"""Helpers to ask a language model for JUnit tests."""

from __future__ import annotations

import os
from typing import Optional

try:
    import openai
except ImportError:  # pragma: no cover - openai may not be installed in tests
    openai = None

try:
    from langchain.chat_models import ChatOpenAI
except Exception:  # pragma: no cover - langchain may not be installed in tests
    ChatOpenAI = None


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
        llm = ChatOpenAI(model_name="gpt-4o", max_tokens=800)
        result = llm.invoke(prompt)
        return result.content.strip()

    if openai is not None:
        api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert Java test writer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()

    # No language model available
    return ""


def generate_junit_test(java_method_code: str) -> str:
    """Return the JUnit test generated for ``java_method_code``."""

    prompt = _craft_prompt(java_method_code)
    return _call_llm(prompt)


if __name__ == "__main__":
    from extract_method import extract_method

    method_code = extract_method("HelloWorld.java")
    print("Extracted Method:\n", method_code)
    junit_test = generate_junit_test(method_code)
    print("\nGenerated JUnit Test:\n", junit_test)
