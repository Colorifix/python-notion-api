from notion_integration.api.utils import get_derived_class
from notion_integration.api.models.properties import (
    TitlePropertyItem,
    RichTextPropertyItem,
    RelationPropertyItem,
    PeoplePropertyItem
)
from notion_integration.api.models.fields import (
    typeField, idField
)
from typing import Optional, Dict, Any


class PropertyItemIterator:

    property_type: Optional[str] = typeField
    property_id: Optional[str] = idField

    _iterator_map = {
        "title": "TitlePropertyItemIterator",
        "rich_text": "RichTextPropertyItemIterator",
        "people": "PeoplePropertyItemIterator",
        "relation": "RelationPropertyItemIterator",
        "rollup": "RollupPropertyItemIterator"
    }

    @property
    def value(self):
        return self.all()

    def __init__(self, generator, property_type, property_id):
        self.generator = generator
        self.property_type = property_type
        self.property_id = property_id

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.generator)

    def all(self):
        return None

    @classmethod
    def from_generator(cls, generator, property_type: str, property_id: str):
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

        return iterator_cls(
            generator,
            property_type,
            property_id
        )

    @classmethod
    def create_new(cls, value):
        """Creates a new property iterator
        Will only create a single item in the iterator
        The type of the value will depend on the particular class.

        """
        obj = cls(iter([]))
        obj.set_value(value)
        return obj


class TitlePropertyItemIterator(PropertyItemIterator):
    iterator_type = 'title'

    def all(self):
        return "".join([item.value for item in self.generator])

    def set_value(self, value):
        self.generator = iter([TitlePropertyItem.create_new(value)])

    def get_dict_for_post(self):
        return {"title": [{"text": {"content": item.value}}
                          for item in self.generator]}


class RichTextPropertyItemIterator(PropertyItemIterator):
    iterator_type = 'rich_text'

    def all(self):
        return "".join([item.value for item in self.generator])

    def set_value(self, value):
        self.generator = iter([
            RichTextPropertyItem.create_new(value)])

    def get_dict_for_post(self):
        return {"rich_text": [{"text": {"content": item.value}}
                              for item in self.generator]}


class PeoplePropertyItemIterator(PropertyItemIterator):
    iterator_type = 'people'

    def all(self):
        return [item.value for item in self.generator]

    def set_value(self, value):
        self.generator = iter([PeoplePropertyItem.create_new(value)])

    def get_dict_for_post(self):
        return {"people": [{"object": 'user', 'id': item.people.user_id}
                           for item in self.generator]}


class RelationPropertyItemIterator(PropertyItemIterator):
    iterator_type = 'relation'

    def all(self):
        return [item.value for item in self.generator]

    def set_value(self, page_id: str):
        self.generator = iter([RelationPropertyItem.create_new(page_id)])

    def get_dict_for_post(self):
        return {"relation": [{'id': item.relation.page_id}
                             for item in self.generator]}


class RollupPropertyItemIterator(PropertyItemIterator):
    iterator_type = 'rollup'

    def all(self):
        return [res.value for res in self.generator]

    def set_value(self, results: Dict[str, Any]):
        self.generator = iter([results])
