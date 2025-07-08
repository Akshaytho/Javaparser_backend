from flask import Flask, request, jsonify
from extract_method import extract_method
from junit_test_generator import generate_junit_test
import os
import io
import zipfile
import base64
import re

# Add CORS support to allow requests from UI
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/generate-tests', methods=['POST'])
def generate_tests():
    """Generate tests for multiple Java source files."""
    # Check if request has JSON data or form data
    if request.is_json:
        data = request.get_json()
        print("Received JSON data:", data)
    else:
        data = request.form.to_dict()
        print("Received form data:", data)
        # Convert form data files to expected format
        if 'files' in data:
            data['files'] = eval(data['files'])
            print("Converted files data:", data['files'])

    if not data or 'files' not in data:
        return jsonify({'error': 'No files provided'}), 400

    files = data['files']
    if not isinstance(files, list):
        return jsonify({'error': 'files must be a list'}), 400

    # Map of output filename to test content
    test_files = {}
    methods_info = {}
    for idx, file in enumerate(files):
        name = file.get('name')
        content = file.get('content')
        print(f"Processing file: {name}")
        if not name or content is None:
            continue

        # Write content to a temporary file so ExtractMethod can parse it
        tmp_name = f"temp_{idx}.java"
        with open(tmp_name, "w") as tmp_file:
            tmp_file.write(content)

        # Extract method bodies using the Java utility
        extracted = extract_method(tmp_name)
        print(f"Extracted methods from {name}:\n{extracted}")
        if not extracted:
            os.remove(tmp_name)
            continue

        # Collect method names for the response
        method_names = re.findall(r"\b(\w+)\s*\(", extracted)
        methods_info[name] = method_names

        junit = generate_junit_test(extracted)
        test_name = name.rsplit('.', 1)[0] + 'Test.java'
        test_files[test_name] = junit
        print(f"Generated test for {name} -> {test_name}")

        os.remove(tmp_name)

    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        for fname, code in test_files.items():
            zf.writestr(fname, code)
            print(f"Added {fname} to zip file")
    mem_zip.seek(0)
    zip_b64 = base64.b64encode(mem_zip.getvalue()).decode("utf-8")

    return jsonify({"zip": zip_b64, "methods": methods_info})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
