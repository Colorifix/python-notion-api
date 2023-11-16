from slugify import slugify as sslugify


def get_derived_class(base_class, derived_cass_name):
    return next(
        (
            cls
            for cls in base_class.__subclasses__()
            if cls.__name__ == derived_cass_name
        ),
        None,
    )


def slugify(string: str):
    return sslugify(string, replacements=[["*", "star"]], separator="_")
