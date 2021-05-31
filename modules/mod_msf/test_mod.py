import unittest
import warnings
from mod import execute
from mock import patch, MagicMock, mock_open


@patch('time.sleep', MagicMock)
class TestModules(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=ResourceWarning)
        warnings.simplefilter('ignore', category=ImportWarning)

        self.args = {}

    @patch('mod.ms')
    @patch('mod.get_session_ids', return_value=[])
    @patch('mod.read_output', return_value='Success test data')
    def test_mod(self, *args):
        self.args.update({'exploit': 'test exploit', 'exploit_arguments': {"RHOSTS": "127.0.0.1"}})

        ret = execute(self.args)

        self.assertEqual(ret.get('return_code'), 0)
        self.assertEqual(ret.get('std_out'), 'Success test data')
        self.assertIsNone(ret.get('mod_err'))
