"""Exercise isolated nft table ownership and atomic validation without root."""
import pathlib
import runpy
import subprocess
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).with_name('forgejo-runner-fence.py')


class RunnerFenceTest(unittest.TestCase):
    def exercise(self, exists):
        calls = []

        def fake(args, **kwargs):
            calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, 0 if exists or len(calls) > 1 else 1)

        with patch('subprocess.run', side_effect=fake):
            runpy.run_path(str(SCRIPT), run_name='__main__')
        self.assertEqual(calls[1][0], ['nft', '-c', '-f', '-'])
        self.assertEqual(calls[2][0], ['nft', '-f', '-'])
        self.assertEqual(calls[1][1]['input'], calls[2][1]['input'])
        rules = calls[2][1]['input']
        self.assertEqual(rules.startswith('delete table'), exists)
        self.assertNotIn('flush', rules)
        self.assertIn('192.168.1.206', rules)
        self.assertIn('10.244.5.249', rules)
        self.assertIn('18116, 18117', rules)
        self.assertIn('counter drop', rules)
        return calls

    def test_first_install(self):
        self.exercise(False)

    def test_reapply_owns_only_its_table(self):
        self.exercise(True)

    def test_validation_failure_does_not_apply(self):
        calls = []

        def fake(args, **kwargs):
            calls.append(args)
            if '-c' in args:
                raise subprocess.CalledProcessError(1, args)
            return subprocess.CompletedProcess(args, 0)

        with patch('subprocess.run', side_effect=fake):
            with self.assertRaises(subprocess.CalledProcessError):
                runpy.run_path(str(SCRIPT), run_name='__main__')
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
