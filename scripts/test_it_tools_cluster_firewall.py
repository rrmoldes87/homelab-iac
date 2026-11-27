"""Read-only guard validation tests; no host firewall commands are executed."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('guard', Path(__file__).with_name('it-tools-cluster-firewall.py'))
assert spec is not None and spec.loader is not None
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def fixture():
    expr = [{'match': {'left': {'payload': {'protocol': 'ip', 'field': 'saddr'}}, 'right': '192.168.1.205'}}, {'accept': None}]
    current = {'nftables': [{'rule': {'expr': expr}}, {'rule': {'expr': [{'drop': None}]}}, {'rule': {'expr': [{'return': None}]}}]}
    parent = {'nftables': [{'rule': {'expr': [{'jump': {'target': 'HM_ITTOOLS'}}]}}]}
    return current, parent


class GuardTests(unittest.TestCase):
    def test_owned_chain(self):
        guard.validate_owned(*fixture())

    def test_unknown_source_refused(self):
        current, parent = fixture()
        current['nftables'][0]['rule']['expr'][0]['match']['right'] = '192.168.1.99'
        with self.assertRaises(RuntimeError):
            guard.validate_owned(current, parent)

    def test_missing_drop_refused(self):
        current, parent = fixture()
        current['nftables'][1]['rule']['expr'] = [{'accept': None}]
        with self.assertRaises(RuntimeError):
            guard.validate_owned(current, parent)

    def test_duplicate_jump_refused(self):
        current, parent = fixture()
        parent['nftables'] *= 2
        with self.assertRaises(RuntimeError):
            guard.validate_owned(current, parent)

    def test_prefix_source(self):
        current, parent = copy.deepcopy(fixture())
        current['nftables'][0]['rule']['expr'][0]['match']['right'] = {'prefix': {'addr': '10.244.0.0', 'len': 24}}
        guard.validate_owned(current, parent)


if __name__ == '__main__':
    unittest.main()
