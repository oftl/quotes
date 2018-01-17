#!/usr/bin/env python3

import bottle
from bottle import request, response, route, post, get, run, template
import logging
import json
import yaml
import random

from quotes.quote import Quote


app = bottle.Bottle(autojson = False)


@app.get ('/quote')
def random_quote ():
    response.set_header ('Content-Type', 'application/vnd.collection+json')
    return wrap_quote (quote = get_quote ())

#http://localhost:8080//quote/1
@app.get ('/quote/<id>')
def quote_by_id (id):
    response.set_header ('Content-Type', 'application/vnd.collection+json')
    return wrap_quote (quote = get_quote (id = id))


def wrap_quote (**kwa):
    quote = kwa.get ('quote')

    item = dict (
        href = mk_url ('/'),
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
                href = mk_url ('/quote/{}/delete'.format (quote.id)),
                prompt = 'Delete this quote'
            ),
            dict (
                rel = 'like',
                href = mk_url ('/quote/{}/delete'.format (quote.id)),
                prompt = 'Like this quote'
            ),
        ],
    )

    return json.dumps (res (items = [item]))


@app.post ('/quotes')
def post_quote ():
    json_data = json.loads (request.body.read())
    template = json_data.get ('template')
    data = template.get ('data')

    author = list (filter (lambda d: d.get ('name') == 'author', data)).pop().get('value')
    text   = list (filter (lambda d: d.get ('name') == 'text', data)).pop().get('value')
    id     = max ([q.id for q in quotes]) + 1

    quote = Quote (author = author, text = text, id = id)
    quotes.append (quote)

    logger.info ('created quote: {}'.format (quote))

    response.set_header ('Content-Type', 'application/vnd.collection+json')
    response.set_header ('Location', mk_url ('/quote/{}'.format (id)))
    response.status = 201

    return

### helpers

def get_config (**kwa):
    configfile = kwa.get ('configfile')

    with open (configfile, 'r') as ymlfile:
        return yaml.load (ymlfile)


def get_logger (**kwa):
    logfile = kwa.get ('logfile')
    logger  = kwa.get ('logger')
    level   = kwa.get ('level') or logging.DEBUG

    handler = logging.FileHandler (logfile)
    handler.setFormatter (logging.Formatter (fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    log = logging.getLogger (logger)
    log.addHandler (handler)
    log.setLevel (level)

    return log


def get_quote (**kwa):
    id = kwa.get ('id')

    if id:
        id = int(id)
        return list (filter (lambda q: q.id == id, quotes)).pop()
    else:
        i = random.randrange (0, len (quotes))
        return quotes[i]


def res (**kwa):
    items = kwa.get ('items')

    return dict (
        collection = dict (
            version = '1.0',
            href = mk_url ('/'),
            links = [
                dict (
                    href   = mk_url ('/'),
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


mk_url = lambda path: '{scheme}://{host}/{path}'.format (
    scheme = request.urlparts[0],
    host   = request.urlparts[1],
    path   = path,
)


### main

config = get_config (configfile = './main.yml')
logger = get_logger (
    logfile = config.get ('logfile'),
    logger  = config.get ('logger'),
    level   = config.get ('level'),
)

quotes = [ Quote (author = 'David Hume', text = 'Programs that write programs are the happiest programs in the world.', id = 1)]

if __name__ == '__main__':
    log ('ready ...')

    app.run (
        host = config.get ('host'),
        port = config.get ('port'),
    )

    log ('... bye')
