from slugify import slugify as sslugify


def slugify(string: str):
    return sslugify(
        string,
        replacements=[['*', 'star']],
        separator='_'
    )
