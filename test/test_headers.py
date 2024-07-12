# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import unittest
from pathlib import Path


class HeadersTester(unittest.TestCase):
    def setUp(self):
        shebang = ["#!usr/bin/python\n"]
        blank_line = "\n"

        copyright_notice = ["# Copyright (C) 2021-2022, Pyronear.\n"]
        license_notice = [
            "# This program is licensed under the Apache License version 2.\n",
            "# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.\n",
        ]

        self.headers = [
            shebang + [blank_line] + copyright_notice + [blank_line] + license_notice,
            copyright_notice + [blank_line] + license_notice,
        ]

        self.excluded_files = ["version.py", "__init__.py"]

    def test_headers(self):
        # For every python file in the repository
        for source_path in Path(__file__).parent.parent.rglob("*.py"):
            if source_path.name not in self.excluded_files:
                # Parse header
                header_length = max(len(option) for option in self.headers)
                current_header = []
                with open(source_path) as f:
                    for idx, line in enumerate(f):
                        current_header.append(line)
                        if idx == header_length - 1:
                            break

                # Compare it
                self.assertTrue(
                    any(
                        "".join(current_header[: min(len(option), len(current_header))]) == "".join(option)
                        for option in self.headers
                    ),
                    msg=f"Invalid header in {source_path}",
                )


if __name__ == "__main__":
    unittest.main()
