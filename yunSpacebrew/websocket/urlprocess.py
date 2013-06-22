from collections import namedtuple

MAX_CACHE_SIZE = 20

uses_params = ['ftp', 'hdl', 'prospero', 'http', 'imap',
               'https', 'shttp', 'rtsp', 'rtspu', 'sip', 'sips',
               'mms', '', 'sftp']
uses_query = ['http', 'wais', 'imap', 'https', 'shttp', 'mms',
              'gopher', 'rtsp', 'rtspu', 'sip', 'sips', '']
uses_fragment = ['ftp', 'hdl', 'http', 'gopher', 'news',
                 'nntp', 'wais', 'https', 'shttp', 'snews',
                 'file', 'prospero', '']

# Characters valid in scheme names
scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

_parse_cache = {}

def urlparse(url, scheme='', allow_fragments=True):
    tuple = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = tuple
    if scheme in uses_params and ';' in url:
        url, params = _splitparams(url)
    else:
        params = ''
    return ParseResult(scheme, netloc, url, params, query, fragment)

def urlsplit(url, scheme='', allow_fragments=True):
    allow_fragments = bool(allow_fragments)
    key = url, scheme, allow_fragments, type(url), type(scheme)
    cached = _parse_cache.get(key, None)
    if cached:
        return cached
    if len(_parse_cache) >= MAX_CACHE_SIZE: # avoid runaway growth
        clear_cache()
    netloc = query = fragment = ''
    i = url.find(':')
    if i > 0:
        if url[:i] == 'http': # optimize the common case
            scheme = url[:i].lower()
            url = url[i+1:]
            if url[:2] == '//':
                netloc, url = _splitnetloc(url, 2)
                if (('[' in netloc and ']' not in netloc) or
                        (']' in netloc and '[' not in netloc)):
                    raise ValueError("Invalid IPv6 URL")
            if allow_fragments and '#' in url:
                url, fragment = url.split('#', 1)
            if '?' in url:
                url, query = url.split('?', 1)
            v = SplitResult(scheme, netloc, url, query, fragment)
            _parse_cache[key] = v
            return v
        for c in url[:i]:
            if c not in scheme_chars:
                break
        else:
            try:
                # make sure "url" is not actually a port number (in which case
                # "scheme" is really part of the path
                _testportnum = int(url[i+1:])
            except ValueError:
                scheme, url = url[:i].lower(), url[i+1:]

    if url[:2] == '//':
        netloc, url = _splitnetloc(url, 2)
        if (('[' in netloc and ']' not in netloc) or
                (']' in netloc and '[' not in netloc)):
            raise ValueError("Invalid IPv6 URL")
    if allow_fragments and scheme in uses_fragment and '#' in url:
        url, fragment = url.split('#', 1)
    if scheme in uses_query and '?' in url:
        url, query = url.split('?', 1)
    v = SplitResult(scheme, netloc, url, query, fragment)
    _parse_cache[key] = v
    return v

def _splitnetloc(url, start=0):
    delim = len(url)   # position of end of domain part of url, default is end
    for c in '/?#':    # look for delimiters; the order is NOT important
        wdelim = url.find(c, start)        # find first of this delim
        if wdelim >= 0:                    # if found
            delim = min(delim, wdelim)     # use earliest delim position
    return url[start:delim], url[delim:]   # return (domain, rest)

def _splitparams(url):
    if '/'  in url:
        i = url.find(';', url.rfind('/'))
        if i < 0:
            return url, ''
    else:
        i = url.find(';')
    return url[:i], url[i+1:]

class ResultMixin(object):
    """Shared methods for the parsed result objects."""

    @property
    def username(self):
        netloc = self.netloc
        if "@" in netloc:
            userinfo = netloc.rsplit("@", 1)[0]
            if ":" in userinfo:
                userinfo = userinfo.split(":", 1)[0]
            return userinfo
        return None

    @property
    def password(self):
        netloc = self.netloc
        if "@" in netloc:
            userinfo = netloc.rsplit("@", 1)[0]
            if ":" in userinfo:
                return userinfo.split(":", 1)[1]
        return None

    @property
    def hostname(self):
        netloc = self.netloc.split('@')[-1]
        if '[' in netloc and ']' in netloc:
            return netloc.split(']')[0][1:].lower()
        elif ':' in netloc:
            return netloc.split(':')[0].lower()
        elif netloc == '':
            return None
        else:
            return netloc.lower()

    @property
    def port(self):
        netloc = self.netloc.split('@')[-1].split(']')[-1]
        if ':' in netloc:
            port = netloc.split(':')[1]
            return int(port, 10)
        else:
            return None

class SplitResult(namedtuple('SplitResult', 'scheme netloc path query fragment'), ResultMixin):

    __slots__ = ()

class ParseResult(namedtuple('ParseResult', 'scheme netloc path params query fragment'), ResultMixin):

    __slots__ = ()