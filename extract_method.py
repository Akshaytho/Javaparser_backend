"""Helpers to run a small Java program that prints all methods in a file."""

import os
import subprocess
import sys
import logging

# Paths to the Java helper and library
_DIR = os.path.dirname(os.path.abspath(__file__))
_JAR = os.path.join(_DIR, "javaparser-core-3.25.4.jar")
_JAVA_FILE = os.path.join(_DIR, "ExtractMethod.java")
_CLASS_FILE = os.path.join(_DIR, "ExtractMethod.class")

logger = logging.getLogger(__name__)


def _ensure_compiled() -> bool:
    """Compile the Java helper once so we can run it later."""

    if os.path.exists(_CLASS_FILE):
        return True

    logger.info("Compiling Java helper")

    cmd = ["javac", "-cp", _JAR, _JAVA_FILE]
    result = subprocess.run(
        cmd,
        cwd=_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        logger.error("Compile error: %s", result.stderr)
        return False
    return True


def extract_method(java_file: str) -> str | None:
    """Return all methods found in ``java_file`` as text."""

    if not _ensure_compiled():
        return None

    logger.info("Extracting methods from %s", java_file)

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
        logger.error("Error running Java helper: %s", result.stderr)
        return None
    output = result.stdout.strip()
    logger.info("Extraction complete: %d bytes", len(output))
    return output


if __name__ == "__main__":
    # Simple manual test when running this file directly
    logging.basicConfig(level=logging.INFO)
    output = extract_method("HelloWorld.java")
    print("Extracted method:\n", output)
