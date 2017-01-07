# -*- coding: utf-8 -*-
"""
    sphinx.util.requests
    ~~~~~~~~~~~~~~~~~~~~

    Simple requests package loader

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from __future__ import absolute_import

import requests
import warnings
import pkg_resources

from six import string_types
from six.moves.urllib.parse import urlsplit
try:
    from requests.packages.urllib3.exceptions import SSLError, InsecureRequestWarning
except ImportError:
    # python-requests package in Debian jessie does not provide ``requests.packages.urllib3``.
    # So try to import the exceptions from urllib3 package.
    from urllib3.exceptions import SSLError, InsecureRequestWarning

# try to load requests[security]
try:
    pkg_resources.require(['requests[security]'])
except (pkg_resources.DistributionNotFound,
        pkg_resources.VersionConflict):
    import ssl
    if not getattr(ssl, 'HAS_SNI', False):
        # don't complain on each url processed about the SSL issue
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecurePlatformWarning)
        warnings.warn(
            'Some links may return broken results due to being unable to '
            'check the Server Name Indication (SNI) in the returned SSL cert '
            'against the hostname in the url requested. Recommended to '
            'install "requests[security]" as a dependency or upgrade to '
            'a python version with SNI support (Python 3 and Python 2.7.9+).'
        )
except pkg_resources.UnknownExtra:
    warnings.warn(
        'Some links may return broken results due to being unable to '
        'check the Server Name Indication (SNI) in the returned SSL cert '
        'against the hostname in the url requested. Recommended to '
        'install requests-2.4.1+.'
    )

useragent_header = [('User-Agent',
                     'Mozilla/5.0 (X11; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0')]


def is_ssl_error(exc):
    """Check an exception is SSLError."""
    if isinstance(exc, SSLError):
        return True
    else:
        args = getattr(exc, 'args', [])
        if args and isinstance(args[0], SSLError):
            return True
        else:
            return False


def _get_tls_cacert(url, config):
    """Get addiotinal CA cert for a specific URL.

    This also returns ``False`` if verification is disabled.
    And returns ``True`` if additional CA cert not found.
    """
    if not config.tls_verify:
        return False

    certs = getattr(config, 'tls_cacerts', None)
    if not certs:
        return True
    elif isinstance(certs, (string_types, tuple)):  # type: ignore
        return certs
    else:
        hostname = urlsplit(url)[1]
        if '@' in hostname:
            hostname = hostname.split('@')[1]

        return certs.get(hostname, True)


def get(url, **kwargs):
    """Sends a GET request like requests.get().

    This sets up User-Agent header and TLS verification automatically."""
    kwargs.setdefault('headers', dict(useragent_header))
    config = kwargs.pop('config', None)
    if config:
        kwargs.setdefault('verify', _get_tls_cacert(url, config))

    with warnings.catch_warnings():
        if not kwargs.get('verify'):
            # ignore InsecureRequestWarning if verify=False
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        return requests.get(url, **kwargs)


def head(url, **kwargs):
    """Sends a HEAD request like requests.head().

    This sets up User-Agent header and TLS verification automatically."""
    kwargs.setdefault('headers', dict(useragent_header))
    config = kwargs.pop('config', None)
    if config:
        kwargs.setdefault('verify', _get_tls_cacert(url, config))

    with warnings.catch_warnings():
        if not kwargs.get('verify'):
            # ignore InsecureRequestWarning if verify=False
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        return requests.get(url, **kwargs)
