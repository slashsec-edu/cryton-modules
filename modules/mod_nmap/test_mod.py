from unittest import TestCase
from mod import execute
from mock import patch, MagicMock


@patch("time.sleep", MagicMock)
class TestModules(TestCase):

    @patch("mod.execute_scan", return_value={
        "127.0.0.1": {
            "ports": [
                {
                    "protocol": "tcp",
                    "portid": "22",
                    "state": "open",
                },
            ],
        },
        "stats": {},
        "runtime": {},
    }

           )
    def test_mod(self, *scanner):
        args = {"target": "127.0.0.1", "ports": [22, 80]}
        ret = execute(args)

        self.assertEqual(ret.get("return_code"), 0)
        self.assertEqual(ret.get("mod_out"), {
            "127.0.0.1": {
                "ports": [
                    {
                        "protocol": "tcp",
                        "portid": "22",
                        "state": "open",
                    },
                ],
            },
        }
                         )
        self.assertIsNone(ret.get("mod_err"))
