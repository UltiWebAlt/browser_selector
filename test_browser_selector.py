import unittest

from browser_selector import build_exec_command


class BuildExecCommandTests(unittest.TestCase):
    def test_firefox_and_zen_receive_the_url(self):
        url = "https://example.com/path?query=value"
        for executable in ("/usr/lib/firefox/firefox", "/opt/zen-browser-bin/zen-bin"):
            with self.subTest(executable=executable):
                self.assertEqual(
                    build_exec_command(f"{executable} %u", [url]),
                    [executable, url],
                )

    def test_expands_embedded_single_url_placeholder(self):
        self.assertEqual(
            build_exec_command("browser --url=%u", ["https://example.com"]),
            ["browser", "--url=https://example.com"],
        )

    def test_expands_multiple_urls(self):
        self.assertEqual(
            build_exec_command("browser %U", ["https://one.example", "https://two.example"]),
            ["browser", "https://one.example", "https://two.example"],
        )


if __name__ == "__main__":
    unittest.main()
