"""Functions meant for user access

All non-Chart related functions are in this module.
For Chart-related functions go in 'factory.py'.

"""
from __future__ import absolute_import

import six
import warnings
import plotly

from . import auth
from . import utils
from .auth import FILE_CONTENT, CONFIG_FILE


pyo = plotly.offline


def go_offline(connected=False):
    """Take plotting offline.

    __PLOTLY_OFFLINE_INITIALIZED is a secret variable
    in plotly/offline/offline.py.

    """
    try:
        pyo.init_notebook_mode(connected)
    except TypeError:
        pyo.init_notebook_mode()

    pyo.__PLOTLY_OFFLINE_INITIALIZED = True


def go_online():
    """Take plotting offline."""
    pyo.__PLOTLY_OFFLINE_INITIALIZED = False


def is_offline():
    """Check online/offline status."""
    return pyo.__PLOTLY_OFFLINE_INITIALIZED


def check_url(url=None):
    """Check URL integrity.

    Parameters
    ----------
        url : string
            URL to be checked.

    """
    if not url:
        if 'http' not in get_config_file()['offline_url']:
            raise Exception("No default offline URL set.\n"
                            "Please run quantmod.set_config_file(offline_url=YOUR_URL) \
                            to set the default offline URL.")
        else:
            url = get_config_file()['offline_url']

    pyo.download_plotlyjs(url)


def ensure_local_files():
    """Ensure that filesystem is setup/filled out in a valid way."""
    if auth.check_file_permissions():
        if not os.path.isdir(AUTH_DIR):
            os.mkdir(AUTH_DIR)
        for fn in [CONFIG_FILE]:
            contents = utils.load_json_dict(fn)
            for key, value in list(FILE_CONTENT[fn].items()):
                if key not in contents:
                    contents[key] = value
            contents_keys = list(contents.keys())
            for key in contents_keys:
                if key not in FILE_CONTENT[fn]:
                    del contents[key]
            utils.save_json_dict(fn, contents)
    else:
        warnings.warn("Looks like you don't have 'read-write' permission to "
                      "your specified Dropbox folder or home ('~') directory.")


def set_config_file(sharing=None, theme=None, dimensions=None,
                    offline=None, offline_url=None,
                    offline_show_link=None, offline_link_text=None):
    """Set the keyword-value pairs in `~/config`.

    Parameters
    ----------
        sharing : string
            Sets the sharing level permission.
                public - anyone can see this chart
                private - only you can see this chart
                secret - only people with the link can see the chart
        theme : string
            Sets the default theme.
            See factory.get_themes() for available themes.
        dimensions : tuple
            Sets the default (width, height) of the chart.
        offline : bool
            If true then the charts are rendered
            locally.
        offline_show_link : bool
            If true then the chart will show a link to
            plot.ly at the bottom right of the chart.
        offline_link_text : string
            Text to display as link at the bottom
            right of the chart.

    """
    if not auth.check_file_permissions():
        raise Exception("You don't have proper file permissions "
                        "to run this function.")

    config = get_config_file()

    if isinstance(sharing, bool):
        if sharing:
            sharing = 'public'
        else:
            sharing = 'private'
    if isinstance(sharing, six.string_types):
        config['sharing'] = sharing
    if isinstance(theme, six.string_types):
        config['theme'] = theme
    if isinstance(dimensions, tuple):
        config['dimensions'] = dimensions
    if isinstance(offline, bool):
        config['offline'] = offline
        if offline:
            go_offline()
    if isinstance(offline_url, six.string_types):
        config['offline_url'] = offline_url
    if isinstance(offline_show_link, six.string_types):
        config['offline_show_link'] = offline_show_link
    if isinstance(offline_link_text, six.string_types):
        config['offline_link_text'] = offline_link_text

    utils.save_json_dict(CONFIG_FILE, config)
    ensure_local_files()


def get_config_file(*args):
    """
    Return specified args from `~/config`. as dict.
    Return all if no arguments are specified.

    Example
    -------
        get_config_file('sharing')

    """
    if auth.check_file_permissions():
        ensure_local_files()
        return utils.load_json_dict(CONFIG_FILE, *args)
    else:
        return FILE_CONTENT[CONFIG_FILE]


def reset_config_file():
    """Reset config file to package defaults."""
    ensure_local_files()  # Make sure what's there is OK
    f = open(CONFIG_FILE, 'w')
    f.close()
    ensure_local_files()


set_credentials_file = plotly.tools.set_credentials_file
get_credentials_file = plotly.tools.get_credentials_file
reset_credentials_file = plotly.tools.reset_credentials_file
