

DEFAULT_CHARSETS = {
    'l': list('abcdefghijklmnopqrstuvwxyz'),
    'u': list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    'd': list('0123456789'),
    'h': list('0123456789abcdef'),
    'H': list('0123456789ABCDEF'),
    's': list(""" !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
}
DEFAULT_CHARSETS['a'] = set(DEFAULT_CHARSETS['l'] + DEFAULT_CHARSETS['u'] + DEFAULT_CHARSETS['d'] + DEFAULT_CHARSETS['s'])


def handler(event, context):

    file_s3_key = event.get('file_s3_key')

    charsets = {}.update(DEFAULT_CHARSETS)

    # Expected format : {'1': 'ABCDEF'}
    custom_charsets = event.get('custom_charsets')
    if custom_charsets:
        charsets.update(custom_charsets)

    mask = event.get('mask')

    # Compute the number of possible characters for each mask items







