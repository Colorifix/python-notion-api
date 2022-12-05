from python_notion_api.models.common import DateObject

from python_notion_api.models.properties import PropertyItem
from python_notion_api.models.blocks import Block


class PropertyItemIterator:
    def __init__(self, generator, property_type, property_id):
        self.generator = generator
        self.property_type = property_type
        self.property_id = property_id
        self._value = None
        self.cache = None

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.generator)

    @property
    def value(self):
        if self._value is None:
            self._value = self._get_value()
        return self._value

    def _get_value(self):
        return [
            PropertyItem.from_obj(item.dict()).value
            for item, _ in self.generator
        ]


class TextPropertyItemIterator(PropertyItemIterator):
    def _get_value(self):
        return "".join([
            PropertyItem.from_obj(item.dict()).value
            for item, _ in self.generator
        ])


class ArrayPropertyItemIterator(PropertyItemIterator):
    pass


class RollupPropertyItemIterator(PropertyItemIterator):
    def _get_value(self):
        items = []
        last_prop = None

        for item, prop in self.generator:
            items.append(item)
            last_prop = prop

        if last_prop is None:
            return None

        prop_type = last_prop["rollup"]["type"]

        if prop_type == "incomplete":
            raise ValueError("Got an incomplete rollup. Sorry")
        elif prop_type == "unsupported":
            raise ValueError("Got an unsupported rollup. Sorry")
        elif prop_type == "array":
            return [
                PropertyItem.from_obj(item.dict()).value
                for item in items
            ]
        elif prop_type == "number":
            return last_prop["rollup"]["number"]
        elif prop_type == "date":
            return DateObject(**last_prop["rollup"]["date"])
        else:
            raise ValueError("Got an unknown rollup type: '{prop_type}'")


def create_property_iterator(generator, property_type, property_id):
    text_property_types = ["title", "rich_text"]

    if property_type == "rollup":
        return RollupPropertyItemIterator(
            generator, property_type, property_id
        )
    elif property_type in text_property_types:
        return TextPropertyItemIterator(generator, property_type, property_id)
    else:
        return ArrayPropertyItemIterator(generator, property_type, property_id)


class BlockIterator:
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self

    def __next__(self):
        next_block = next(self.generator)
        if isinstance(next_block, tuple):
            next_block = next_block[0]
        return Block.from_obj(next_block.dict(by_alias=True))
