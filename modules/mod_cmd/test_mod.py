import unittest
import warnings
from mock import patch, MagicMock
import importlib


class FakeProcess:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout.encode()
        self.stderr = stderr.encode()

    def check_returncode(self):
        return 0

    def kill(self):
        pass


@patch('time.sleep', MagicMock)
class TestModules(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=ResourceWarning)
        warnings.simplefilter('ignore', category=ImportWarning)

        self.args = {'arguments': {}, 'target': '10.0.3.5'}

    @patch('subprocess.run', return_value=FakeProcess(0, "test out", "test err"))
    @patch('mod.open', MagicMock())
    def test_mod(self, *args):
        module_name = "mod"
        module_obj = importlib.import_module(module_name)
        self.args.update({'arguments': {'mod': 'test'}})

        ret = module_obj.execute(self.args)

        self.assertEqual(ret.get('return_code'), 0)
        self.assertTrue(ret.get('std_out').startswith("log_cmd"))
        self.assertIsNone(ret.get('std_err'))
