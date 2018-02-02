#!/usr/bin/env python3

from bottle import Bottle, request, response, route, post, get, run, template
import logging
import json
import yaml
import random

from quotes.quotes_types import Quote
from quotes.quotes import Quotes


class API (Bottle):
    """ simple fortune-like quotes server
    """

    def __init__ (self):
        super (API, self).__init__()

        self.quotes = Quotes()

        self.route ('/',            method = 'GET',  callback = self.random_quote)
        self.route ('/quote',       method = 'GET',  callback = self.random_quote)
        self.route ('/quote/<id>',  method = 'GET',  callback = self.quote_by_id)
        self.route ('/quotes',      method = 'GET',  callback = self.all_quotes)
        self.route ('/quotes',      method = 'POST', callback = self.post_quote)
        self.route ('/quote/<id>',  method = 'DELETE', callback = self.delete_quote)

        self.route ('/search',      method = 'GET',   callback = self.search)

        self.config = self.get_config (configfile = 'quotes/api.yml')
        self.logger = self.get_logger (
            logfile = self.config.get ('logfile'),
            logger  = self.config.get ('logger'),
            level   = self.config.get ('level'),
        )


    def mk_url (self, path = None):
        url = '{scheme}://{host}'.format (
            scheme = request.urlparts[0],
            host   = request.urlparts[1],
        )

        if path:
            url += '/%s' % path

        return url


    def start (self):
        """ start quotes server
        """

        self.logger.info ('ready ...')

        self.run (
            host = self.config.get ('host'),
            port = self.config.get ('port'),
        )

        self.logger.info ('... bye')


    def search (self):
        term = request.query.search

        response.set_header ('Content-Type', 'application/vnd.collection+json')

        return json.dumps (self.res (items = [
            self.wrap_quote (
                quote = q
            )
            for q in self.quotes.search (term = term)
        ]))


    def random_quote (self):
        """ get a random quote
        """

        response.set_header ('Content-Type', 'application/vnd.collection+json')

        return json.dumps (self.res (items = [
            self.wrap_quote (
                quote = self.quotes.random_quote ()
            )
        ]))

    def quote_by_id (self, id):
        """ get quote identified by its id
        """

        response.set_header ('Content-Type', 'application/vnd.collection+json')
        return json.dumps (self.res (items = [
            self.wrap_quote (
                quote = self.quotes.quote_by_id (id = id)
            )
        ]))


    def all_quotes (self):
        """ get quote identified by its id
        """

        response.set_header ('Content-Type', 'application/vnd.collection+json')
        return json.dumps (self.res (items = [
            self.wrap_quote (
                quote = q
            )
            for q in self.quotes.all_quotes()
        ]))


    def wrap_quote (self, **kwa):
        """ wrap the given quote in a collection+json structure
        """

        quote = kwa.get ('quote')

        item = dict (
            href = self.mk_url (),
            data = [
                dict (
                    name = 'author',
                    value = quote.author,
                    prompt = 'Author',
                ),
                dict (
                    name = 'text',
                    value = quote.text,
                    prompt = 'Text',
                ),
                dict (
                    name = 'id',
                    value = quote.id,
                    prompt = 'ID',
                ),
            ],
            links = [
                dict (
                    rel = 'origin',
                    href = 'https://duckduckgo/search={}'.format (quote.text),
                    prompt = 'Origins of this quote'
                ),
            ],
        )

        return item


    def post_quote (self):
        """ add a new quote
        """

        json_data = json.loads (request.body.read())
        template = json_data.get ('template')
        data = template.get ('data')

        author = list (filter (lambda d: d.get ('name') == 'author', data)).pop().get('value')
        text   = list (filter (lambda d: d.get ('name') == 'text', data)).pop().get('value')

        id = self.quotes.add_quote (
            author = author,
            text = text,
        )

        self.logger.info ('created quote with id: {}'.format (id))

        response.set_header ('Content-Type', 'application/vnd.collection+json')
        response.set_header ('Location', self.mk_url ('quote/{}'.format (id)))
        response.status = 201

        return


    def delete_quote (self, id):
        """ delete quote identified by id
        """

        self.quotes.delete_quote (id = id)

        response.status = 204
        response.set_header ('Content-Type', 'application/vnd.collection+json')

        return

    ### helpers

    def get_config (self, **kwa):
        """ load configuration from given file
        """

        configfile = kwa.get ('configfile')

        with open (configfile, 'r') as ymlfile:
            return yaml.load (ymlfile)


    def get_logger (self, **kwa):
        """ create and return a logger
        """

        logfile = kwa.get ('logfile')
        logger  = kwa.get ('logger')
        level   = kwa.get ('level') or logging.DEBUG

        handler = logging.FileHandler (logfile)
        handler.setFormatter (logging.Formatter (fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        log = logging.getLogger (logger)
        log.addHandler (handler)
        log.setLevel (level)

        return log


    def res (self, **kwa):
        """ top-level collection+josn
        """

        items = kwa.get ('items')

        return dict (
            collection = dict (
                version = '1.0',
                href = self.mk_url (),
                links = [
                    dict (
                        href   = self.mk_url ('/quote'),
                        rel    = 'root',
                        prompt = 'Get a quote',
                        render = 'link',
                    ),
                    dict (
                        href   = self.mk_url ('/quotes'),
                        rel    = 'root',
                        prompt = 'Get all quote',
                        render = 'link',
                    ),
                ],
                items = items,
                queries = [
                    dict (
                        href   = self.mk_url ('search'),
                        rel    = 'search',
                        prompt = 'Enter search string',
                        data = [dict (
                            name  = 'search',
                            value = '',
                        )]
                    ),
                ],
                template = dict (
                    data = [
                        dict (name = 'author', value = '', prompt = 'Author'),
                        dict (name = 'text', value = '', prompt = 'Text'),
                    ]
                ),
                error = None,
            ),
        )
