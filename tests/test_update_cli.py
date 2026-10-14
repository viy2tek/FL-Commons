import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fl_commons.cli import main


class UpdateCliTests(unittest.TestCase):
    def test_updates_do_not_require_fl_bearer_token_and_policy_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('fl_commons.updates.update_directory', return_value=Path(directory)), \
                 patch.dict('os.environ', {'FL_COMMONS_TOKEN': ''}), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                main(['updates', 'status'])
                self.assertEqual(json.loads(output.getvalue())['policy'], 'manual')
                output.truncate(0)
                output.seek(0)
                main(['updates', 'policy', 'automatic'])
                self.assertEqual(json.loads(output.getvalue())['policy'], 'automatic')
