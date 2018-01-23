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
        self.route ('/quotes',      method = 'POST', callback = self.post_quote)

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

    def random_quote (self):
        """ get a random quote
        """

        response.set_header ('Content-Type', 'application/vnd.collection+json')
        return self.wrap_quote (quote = self.quotes.random_quote ())

    def quote_by_id (self, id):
        """ get quote identified by its id
        """

        response.set_header ('Content-Type', 'application/vnd.collection+json')
        return self.wrap_quote (quote = self.quotes.quote_by_id (id = id))


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
                    rel = 'delete',
                    href = self.mk_url ('quote/{}/delete'.format (quote.id)),
                    prompt = 'Delete this quote'
                ),
                dict (
                    rel = 'like',
                    href = self.mk_url ('quote/{}/delete'.format (quote.id)),
                    prompt = 'Like this quote'
                ),
            ],
        )

        return json.dumps (self.res (items = [item]))


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
                        href   = self.mk_url (),
                        rel    = 'root',
                        prompt = 'Get a quote',
                        render = 'link',
                        # name   = 'random',
                    ),
                ],
                items = items,
                queries = None,
                template = dict (
                    data = [
                        dict (name = 'author', value = '', prompt = 'Author'),
                        dict (name = 'text', value = '', prompt = 'Text'),
                    ]
                ),
                error = None,
            ),
        )
