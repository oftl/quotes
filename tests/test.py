import unittest
from webtest import TestApp
import json

from quotes.api import API

class Test_Quote (unittest.TestCase):

    def test (self):
        app = TestApp (API ())

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

        # all quotes

        res = app.get ('http://localhost:8080/quotes',
            status = 200,
        )

        self.assertEqual (2, len (res.json_body.get('collection').get('items')))
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

        res = app.get ('http://localhost:8080/search?search=garfield',
            status = 200,
        )
        self.assertEqual (1, len (res.json_body.get('collection').get('items')))

        res = app.get ('http://localhost:8080/search?search=odie',
            status = 200,
        )
        self.assertEqual (0, len (res.json_body.get('collection').get('items')))

        res = app.delete ('http://localhost:8080/quote/3',
            status = 204,
        )

if __name__ == '__main__':
    unittest.main()
