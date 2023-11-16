from python_notion_api.models.blocks import Block
from python_notion_api.models.common import DateObject
from python_notion_api.models.properties import PropertyItem
from python_notion_api.utils import get_derived_class


class PropertyItemIterator:
    def __init__(self, generator, property_item):
        self.generator = generator
        self.property_item = property_item
        self.property_type = property_item.property_type
        self.property_id = property_item.property_id
        self._value = None

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
        prop_cls = get_derived_class(
            PropertyItem, PropertyItem._class_map.get(self.property_type)
        )
        return prop_cls(
            id=self.property_id,
            init=[
                getattr(item, self.property_type) for item, _ in self.generator
            ],
        ).value


class RollupPropertyItemIterator(PropertyItemIterator):
    def _get_value(self):
        items = []
        prop_type = self.property_item.rollup.rollup_type
        last_prop = None

        for item, prop in self.generator:
            items.append(item)
            last_prop = prop

        if prop_type == "incomplete":
            raise ValueError("Got an incomplete rollup. Sorry")
        elif prop_type == "unsupported":
            raise ValueError("Got an unsupported rollup. Sorry")
        elif prop_type == "array":
            return [
                get_derived_class(
                    PropertyItem,
                    PropertyItem._class_map.get(item.property_type),
                )(id=self.property_id, init=getattr(item, item.property_type))
                for item in items
            ]
        elif prop_type == "number":
            return last_prop and last_prop["rollup"]["number"]
        elif prop_type == "date":
            date = last_prop and last_prop["rollup"]["date"]
            if date is not None:
                return DateObject(**date)
            else:
                return None

        else:
            raise ValueError("Got an unknown rollup type: '{prop_type}'")


def create_property_iterator(generator, property_item):
    if property_item.property_type == "rollup":
        return RollupPropertyItemIterator(generator, property_item)
    else:
        return PropertyItemIterator(generator, property_item)


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
