# Java Parser Demo Backend

This repository provides a simple backend service for generating JUnit tests
from Java source code. The service exposes a small Flask API that extracts
methods using `javaparser` and generates tests via an LLM.

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

The backend optionally integrates with **LangChain** and **LangSmith** for LLM
invocation and tracing. If these packages are unavailable, the server falls
back to using the raw OpenAI client.

A Java runtime is required for the `ExtractMethod` class. Make sure the
`javaparser-core-3.25.4.jar` is present in the repository.

Set the `OPENAI_API_KEY` environment variable if you want to use the OpenAI
API for generating tests.

## Running the server

```bash
python app.py
```

Send a POST request to `/generate-tests` with a JSON payload containing a list
of files. Each file must include a `name` and `content` field. The server will
extract the methods using the included Java utility and invoke an LLM to
produce JUnit tests for each file. The response returns a JSON object with a
Base64-encoded zip archive (`zip`) and the extracted method names.

Example:

```bash
curl -X POST http://localhost:8000/generate-tests -H 'Content-Type: application/json' \
    -d '{"files": [{"name": "HelloWorld.java", "content": "..."}]}'
```

Decode the `zip` field to retrieve the generated test files.
