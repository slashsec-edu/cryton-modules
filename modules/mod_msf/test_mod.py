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

        self.args = {'arguments': {}, 'target': '10.0.3.5'}

    @patch('mod.ms')
    @patch('mod.get_session_ids', return_value=[])
    def test_mod(self, *args):
        module_name = "mod"
        module_obj = importlib.import_module(module_name)
        self.args.update({'arguments': {'exploit': 'test exploit'}})

        ret = module_obj.execute(self.args)

        self.assertEqual(ret.get('return_code'), 0)
        self.assertEqual(ret.get('std_out'), 'Success test data')
        self.assertIsNone(ret.get('std_err'))
