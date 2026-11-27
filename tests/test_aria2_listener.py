import importlib.util
import pathlib
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('listener', pathlib.Path(__file__).parents[1] / 'scripts/aria2-listener-config.py')
LISTENER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LISTENER)


class ListenerTests(unittest.TestCase):
    def test_secret_options_and_idempotency(self):
        with tempfile.TemporaryDirectory() as root:
            p = pathlib.Path(root) / 'config'
            p.write_text('rpc-secret=test-only\nrpc-listen-all=false\nother=value\n')
            LISTENER.configure(p)
            first = p.read_text()
            LISTENER.configure(p)
            self.assertEqual(first, p.read_text())
            self.assertIn('rpc-secret=test-only\n', first)
            self.assertIn('other=value\n', first)
            self.assertEqual(first.count('rpc-listen-all=true'), 1)

    def test_missing_or_empty_secret_is_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as root:
            p = pathlib.Path(root) / 'config'
            for original in ['enable-rpc=true\n', 'rpc-secret=\n']:
                p.write_text(original)
                with self.assertRaises(ValueError):
                    LISTENER.configure(p)
                self.assertEqual(p.read_text(), original)


if __name__ == '__main__':
    unittest.main()
