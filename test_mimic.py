import unittest

from helga_mimic import is_channel_or_user


class ChannelOrUserTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_channel(self):
        """
        is_channel_or_user returns `True` for channels
        """

        self.assertTrue(is_channel_or_user('#test'))
        self.assertTrue(is_channel_or_user('##test-ot'))

    def test_user(self):
        """
        is_channel_or_user returns `False` for users
        """

        self.assertFalse(is_channel_or_user('aineko'))
