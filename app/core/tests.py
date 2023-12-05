from django.test import TestCase
from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError


class WaitForDBTests(TestCase):
    '''test the wait_for_db command when database is available or not'''

    def test_db_available(self):
        '''test when DB is available'''
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 1)

    @patch("time.sleep", return_value=True)
    def test_db_not_available(self, ts):
        '''test the wait_for_db command when database is only available
        after a few attempts'''
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 6)
