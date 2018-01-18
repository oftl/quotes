import unittest
from webtest import TestApp
import json

from quotes.quotes import Quotes

class Test_Quote (unittest.TestCase):

    def test (self):
        app = TestApp (Quotes ())

        # random quote

        res = app.get ('http://localhost:8080/quote',
            status = 200,
        )

        self.assertEqual (1, len (res.json_body.get('collection').get('items')))
        self.assertEqual (res.content_type, 'application/vnd.collection+json')

        # specific quote

        res = app.get ('http://localhost:8080/quote/1',
            status = 200,
        )

        self.assertEqual (1, len (res.json_body.get('collection').get('items')))
        self.assertEqual (res.content_type, 'application/vnd.collection+json')

        # new quote

        res = app.post ('http://localhost:8080/quotes',
            json.dumps (dict (
                template = dict (
                    data = [
                        dict (name = 'author',value = 'jim'),
                        dict (name = 'text',  value = 'i love garfield'),
                    ]
                ),
            )),
            status = 201,
        )

        self.assertEqual (res.status_int, 201)
        self.assertEqual (res.content_type, 'application/vnd.collection+json')

        res = app.get ('http://localhost:8080/quote/2',
            status = 200,
        )

        self.assertEqual (1, len (res.json_body.get('collection').get('items')))
        self.assertEqual (res.content_type, 'application/vnd.collection+json')


if __name__ == '__main__':
    unittest.main()
