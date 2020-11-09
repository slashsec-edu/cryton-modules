import unittest
import warnings
from mock import patch, MagicMock
import importlib


@patch('time.sleep', MagicMock)
class TestModules(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=ResourceWarning)
        warnings.simplefilter('ignore', category=ImportWarning)

        self.args = {'arguments': {}, 'target': '10.0.3.5'}

    @patch('mod.nmap.PortScanner', MagicMock)
    @patch('csv.DictReader', return_value=[{'port': "22", 'state': 'open'}, {'port': "443", 'state': 'open'}])
    def test_mod(self, *scanner):
        module_name = "mod"
        module_obj = importlib.import_module(module_name)
        self.args.update({'arguments': {"ports": [22, 443]}})

        ret = module_obj.execute(self.args)

        self.assertEqual(ret.get('return_code'), 0)
        self.assertIn('"port": "22"', ret.get('std_out'))
        self.assertIsNone(ret.get('std_err'))
