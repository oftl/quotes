import unittest
from webtest import TestApp

from quotes.main import Main

class Test_Quote (unittest.TestCase):

    def test (self):
        app = TestApp (Main())

        res = app.get ('http://localhost:8080/quote',
            status = 200,
        )

        self.assertEqual (len (res.json_body.get('collection').get('items')), 1)

        # FIXME
        #
        #  res = app.post ('http://localhost:8080/quotes', dict (
        #      template = dict (
        #          data = [
        #              dict (name = 'author',value = 'jim'),
        #              dict (name = 'text',  value = 'i love garfield'),
        #          ]
        #      ),
        #      status = 201,
        #  ))
        #
        #  self.assertEqual (len (res.json_body.get('collection').get('items')), 2)


if __name__ == '__main__':
    unittest.main()
