import unittest

import emoji

import bot


class MyTestCase(unittest.TestCase):

    def test_process_message_greeting(self):
        res = bot.process_message('good morning')
        self.assertIsNotNone(res)
        self.assertEqual(emoji.emojize('Hello Bunmi :blush:',language='alias'),res.text)


if __name__ == '__main__':
    unittest.main()
