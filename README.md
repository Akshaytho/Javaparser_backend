# Java Parser Demo Backend

This repository provides a simple backend service for generating JUnit tests
from Java source code. The service exposes a small Flask API that extracts
methods using `javaparser` and generates tests via an LLM.

## Requirements

1. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install a Java Development Kit (JDK) so that `java` and `javac` are available.
   The helper `ExtractMethod.java` is compiled automatically on the first run
   if `ExtractMethod.class` is missing. Keep `javaparser-core-3.25.4.jar`
   alongside the sources.

3. Set the required environment variables:
   - `OPENAI_API_KEY` to enable the OpenAI API.
   - Optional LangChain/LangSmith variables `LANGCHAIN_TRACING_V2`,
     `LANGCHAIN_ENDPOINT`, `LANGCHAIN_API_KEY` and `LANGCHAIN_PROJECT`.

The backend optionally integrates with **LangChain** and **LangSmith** for LLM
invocation and tracing. If these packages are unavailable, the server falls
back to using the raw OpenAI client.

## Running the server

```bash
python app.py
```

Send a POST request to `/generate-tests` with a list of files. Each file must
include a `name` and `content` field. The server extracts methods with the
Java helper and invokes an LLM to produce JUnit tests for each file. The
response returns a JSON object with a Base64-encoded zip archive (`zip`) and
the extracted method names.

Example JSON request:

```bash
curl -X POST http://localhost:8000/generate-tests -H 'Content-Type: application/json' \
    -d '{"files": [{"name": "HelloWorld.java", "content": "..."}]}'
```

Example multipart/form-data request:

```bash
curl -X POST http://localhost:8000/generate-tests \
    -F 'files=[{"name": "HelloWorld.java", "content": "..."}]'
```

Decode the `zip` field to retrieve the generated test files.
