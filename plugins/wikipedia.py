"""
    Search and display Wikipedia articles
"""

from plugins.commands import command

from urllib.parse import quote_plus
from urllib.request import urlopen
from re import sub
import json

def wikisearch(msg):
    url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&srprop=timestamp&format=json"

    query = json.loads(urlopen(url.format(quote_plus(msg)), timeout = 7).read().decode('UTF-8'))
    query = [x['title'] for x in query['query']['search'][:5]]

    # Removing the [] that surround our titles for channel printing.
    return str(query)[1:-1]


def wikiget(msg):
        url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&titles={}&redirects=true"

        text = json.loads(urlopen(url.format(quote_plus(msg)), timeout = 7).read().decode('UTF-8'))

        # One of the keys is just a random number that we can't/won't predict.
        key = list(text['query']['pages'])[0]

        # We also need to remove all the html formatting from the text.
        text = sub(r'\<.*?>|\n','', text['query']['pages'][key]['extract'])

        return "{}... - https://en.wikipedia.org/wiki/{}".format(text[:200], msg)


@command
def wikipedia(irc, nick, chan, msg, args):
    '''
    Search and display wikipedia articles.
    .wiki <terms>        - Fetch article by exact name.
    .wiki search <terms> - Fetch list of closely matching articles.
    '''
    if not msg:
        return "Need terms to search for, or an exact article title."

    try:
        command, *args = msg.split(' ', 1)
        commands = {
            'search': lambda: wikisearch(args[0])
        }

        if command in commands:
            return commands[command]()

        # Exact match instead of search.
        return wikiget(msg)

    except Exception as e:
        return "There was an error in this module."
