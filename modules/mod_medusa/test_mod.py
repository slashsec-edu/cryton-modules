from unittest import TestCase
from mock import patch, MagicMock, Mock
from mod import execute


@patch('time.sleep', MagicMock())
class TestModules(TestCase):

    @patch('os.remove', MagicMock())
    def test_mod(self, *args):
        args = {'target': '10.0.3.7', 'username': 'test', 'password': 'test', 'output_file': True}
        mock_run = Mock()
        mock_run.stdout = b"ACCOUNT FOUND: [ssh] Host: 127.0.0.1 User: testlogin Password: testpass [SUCCESS]"
        mock_run.stderr = b"error"
        with patch('subprocess.run', return_value=mock_run):
            ret = execute(args)
        self.assertEqual(ret.get('return_code'), 0)
        self.assertEqual(ret.get('std_out'), 'Output file saved in evidence dir')
        self.assertEqual(ret.get('mod_out'), {'username': 'testlogin', 'password': 'testpass'})