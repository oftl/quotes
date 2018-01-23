#!/usr/bin/env python3

import logging
import json
import yaml
import random

from quotes.quotes_types import Quote


class Quotes ():
    """ simple fortune-like quotes server
    """

    def __init__ (self):
        self.config = self.get_config (configfile = 'quotes/quotes.yml')
        self.logger = self.get_logger (
            logfile = self.config.get ('logfile'),
            logger  = self.config.get ('logger'),
            level   = self.config.get ('level'),
        )

        self._quotes = [
            Quote (author = 'David Hume', text = 'Programs that write programs are the happiest programs in the world.', id = 1),
            Quote (author = 'unknown', text = 'Smear the road with a runner!!', id = 2)
        ]


    def random_quote (self):
        """ get a random quote
        """

        return self.get_quote()


    def quote_by_id (self, id):
        """ get quote identified by its id
        """

        return self.get_quote (id = id)


    def add_quote (self, **kwa):
        """ add a new quote
        """

        author = kwa.get ('author')
        text   = kwa.get ('text')
        id     = max ([q.id for q in self._quotes]) + 1

        quote = Quote (author = author, text = text, id = id)
        self._quotes.append (quote)

        return id


    def get_quote (self, **kwa):
        """ return a random quote from the internal storage
            when kwa.id is given that quote is returned instead
        """

        id = kwa.get ('id')

        if id:
            id = int(id)
            return list (filter (lambda q: q.id == id, self._quotes)).pop()
        else:
            i = random.randrange (0, len (self._quotes))
            return self._quotes[i]


    def all_quotes (self):
        """ return all available quotes
        """

        return self._quotes

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
