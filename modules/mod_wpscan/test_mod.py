import unittest
import warnings
from mock import patch, MagicMock, mock_open
import importlib


@patch('time.sleep', MagicMock)
class TestModules(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=ResourceWarning)
        warnings.simplefilter('ignore', category=ImportWarning)

        self.args = {'target': '10.0.3.5'}

    @patch('subprocess.Popen')
    @patch('mod.open', mock_open(read_data="Finished:"))
    def test_mod(self, *args):
        module_name = "mod"
        module_obj = importlib.import_module(module_name)

        ret = module_obj.execute(self.args)

        self.assertEqual(ret.get('return_code'), 0)
        self.assertTrue(ret.get('std_out').startswith('/tmp/report_wpscan'))
        self.assertIsNone(ret.get('mod_err'))
