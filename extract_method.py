import subprocess
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_JAR = os.path.join(_DIR, "javaparser-core-3.25.4.jar")
_JAVA_FILE = os.path.join(_DIR, "ExtractMethod.java")
_CLASS_FILE = os.path.join(_DIR, "ExtractMethod.class")


def _ensure_compiled():
    """Compile the ExtractMethod utility if the class file is missing."""
    if os.path.exists(_CLASS_FILE):
        return True
    cmd = ["javac", "-cp", _JAR, _JAVA_FILE]
    result = subprocess.run(
        cmd,
        cwd=_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        print("Compile error:", result.stderr, file=sys.stderr)
        return False
    return True


def extract_method(java_file):
    """Run the ExtractMethod Java utility on ``java_file``."""
    if not _ensure_compiled():
        return None
    classpath = f"{_DIR}{os.pathsep}{_JAR}"
    cmd = ["java", "-cp", classpath, "ExtractMethod", java_file]
    result = subprocess.run(
        cmd,
        cwd=_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        print("Error:", result.stderr)
        return None
    return result.stdout.strip()

if __name__ == "__main__":
    # Test with your sample file
    output = extract_method('HelloWorld.java')
    print("Extracted method:\n", output)

