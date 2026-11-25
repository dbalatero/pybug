"""Run the locker tests with color in interactive terminals."""

import os
import sys
import unittest


class TerminalOutput:
    def __init__(self, stream):
        self.stream = stream

    def write(self, text):
        label = text.strip()
        if label in {"ok", "OK"}:
            text = f"\033[32m{text}\033[0m"
        elif label.startswith(("FAIL", "ERROR", "AssertionError:")):
            text = f"\033[31m{text}\033[0m"
        return self.stream.write(text)

    def flush(self):
        self.stream.flush()


if __name__ == "__main__":
    output = sys.stderr
    if output.isatty() and not os.environ.get("NO_COLOR"):
        output = TerminalOutput(output)
    runner = unittest.TextTestRunner(stream=output, verbosity=2)
    unittest.main(module=None, testRunner=runner)
