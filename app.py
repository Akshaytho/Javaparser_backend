"""Flask server that generates JUnit tests from Java source files."""

from flask import Flask, request, jsonify
from flask_cors import CORS

import base64
import io
import os
import re
import zipfile

from extract_method import extract_method
from junit_test_generator import generate_junit_test

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


app = Flask(__name__)
# Allow requests from the browser UI
CORS(app)


def _parse_request(req):
    """Return the JSON body for either JSON or form-data requests."""
    if req.is_json:
        return req.get_json()
    data = req.form.to_dict()
    if "files" in data:
        # The form sends a string representation of the list
        data["files"] = eval(data["files"])
    return data


def _process_file(info, idx):
    """Create a test file for a single Java source file."""
    name = info.get("name")
    content = info.get("content")
    if not name or content is None:
        return None

    # Write the source code to a temporary file
    tmp_name = f"temp_{idx}.java"
    with open(tmp_name, "w") as f:
        f.write(content)

    # Ask the Java helper to extract all methods
    extracted = extract_method(tmp_name)
    os.remove(tmp_name)
    if not extracted:
        return None

    # Find all method names for the response
    method_names = re.findall(r"\b(\w+)\s*\(", extracted)

    # Use the LLM to craft a JUnit test
    junit_code = generate_junit_test(extracted)

    test_name = name.rsplit(".", 1)[0] + "Test.java"
    return test_name, junit_code, name, method_names


def _make_zip(test_files):
    """Return a base64 zip archive from a mapping of filename -> code."""
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, code in test_files.items():
            zf.writestr(fname, code)
    mem_zip.seek(0)
    return base64.b64encode(mem_zip.getvalue()).decode("utf-8")


@app.route("/generate-tests", methods=["POST"])
@traceable
def generate_tests():
    """Generate JUnit tests for each file in the request."""
    data = _parse_request(request)
    if not data or "files" not in data:
        return jsonify({"error": "No files provided"}), 400

    files = data["files"]
    if not isinstance(files, list):
        return jsonify({"error": "files must be a list"}), 400

    test_files = {}
    methods_info = {}

    for idx, file_info in enumerate(files):
        result = _process_file(file_info, idx)
        if result is None:
            continue
        test_name, junit, orig_name, names = result
        test_files[test_name] = junit
        methods_info[orig_name] = names

    zip_b64 = _make_zip(test_files)
    return jsonify({"zip": zip_b64, "methods": methods_info})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
