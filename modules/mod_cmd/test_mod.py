from unittest import TestCase
from mock import patch, MagicMock, Mock
from mod import execute


@patch('time.sleep', MagicMock())
class TestModules(TestCase):

    @patch('os.remove', MagicMock())
    def test_mod(self, *args):
        args = {'cmd': "test"}
        mock_run = Mock()
        mock_run.stdout = b"output"
        mock_run.stderr = b"error"
        with patch('subprocess.run', return_value=mock_run):
            ret = execute(args)
        self.assertEqual(ret.get('return_code'), 0)
        self.assertEqual(ret.get('std_out'), 'output')
        self.assertEqual(ret.get('mod_err'), 'error')
