from flask import Flask, request, jsonify
from extract_method import extract_method
from junit_test_generator import generate_junit_test
import os
import io
import zipfile
import base64
import re
from concurrent.futures import ThreadPoolExecutor

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

    def _process(idx_file):
        idx, file = idx_file
        name = file.get('name')
        content = file.get('content')
        print(f"Processing file: {name}")
        if not name or content is None:
            return None

        tmp_name = f"temp_{idx}.java"
        with open(tmp_name, "w") as tmp_file:
            tmp_file.write(content)

        extracted = extract_method(tmp_name)
        print(f"Extracted methods from {name}:\n{extracted}")
        os.remove(tmp_name)
        if not extracted:
            return None

        method_names = re.findall(r"\b(\w+)\s*\(", extracted)
        junit = generate_junit_test(extracted)
        test_name = name.rsplit('.', 1)[0] + 'Test.java'
        return (test_name, junit, name, method_names)

    with ThreadPoolExecutor(max_workers=min(4, len(files))) as executor:
        for result in executor.map(_process, enumerate(files)):
            if result is None:
                continue
            test_name, junit, orig_name, names = result
            test_files[test_name] = junit
            methods_info[orig_name] = names
            print(f"Generated test for {orig_name} -> {test_name}")

    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname, code in test_files.items():
            zf.writestr(fname, code)
            print(f"Added {fname} to zip file")
    mem_zip.seek(0)
    zip_b64 = base64.b64encode(mem_zip.getvalue()).decode("utf-8")

    return jsonify({"zip": zip_b64, "methods": methods_info})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
