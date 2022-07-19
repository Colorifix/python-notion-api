from notion_integration.api.utils import get_derived_class


class PropertyItemIterator:

    _iterator_map = {
        "title": "TitlePropertyItemIterator",
        "rich_text": "RichTextPropertyItemIterator",
        "people": "PeoplePropertyItemIterator",
        "relation": "RelationPropertyItemIterator",
        "rollup": "RollupPropertyItemIterator"
    }

    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.generator)

    def all(self):
        return None

    @classmethod
    def from_generator(cls, generator, property_type: str):
        iterator_type_cls_name = cls._iterator_map.get(property_type, None)

        if iterator_type_cls_name is None:
            raise ValueError(
                f"Unknown property type '{property_type}'"
            )
        iterator_cls = get_derived_class(
            PropertyItemIterator, iterator_type_cls_name
        )

        if iterator_cls is None:
            raise ValueError(
                f"Failed to locate {iterator_type_cls_name}"
            )

        return iterator_cls(generator)


class TitlePropertyItemIterator(PropertyItemIterator):
    def all(self):
        return "".join([item.value for item in self.generator])


class RichTextPropertyItemIterator(PropertyItemIterator):
    def all(self):
        return "".join([item.value for item in self.generator])


class PeoplePropertyItemIterator(PropertyItemIterator):
    def all(self):
        return [item.value for item in self.generator]


class RelationPropertyItemIterator(PropertyItemIterator):
    def all(self):
        return [item.value for item in self.generator]


class RollupPropertyItemIterator(PropertyItemIterator):
    def all(self):
        return []
