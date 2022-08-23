from typing import Optional, List, Dict, Literal, Union, Tuple, Any
from abc import ABC, abstractmethod

from datetime import datetime
from datetime import date as date_type

from pydantic import Field
import pydantic

from notion_integration.api.models.fields import (
    idField, typeField
)

from notion_integration.api.models.common import (
    RichTextObject
)

from notion_integration.api.models.values import (
    DatePropertyValue,
    SelectValue,
    FormulaValue,
    PageReferenceValue,
    RollupValue,
    StatusValue,
    FileReferenceValue
)

from notion_integration.api.models.objects import (
    User,
    NotionObject
)

from notion_integration.api.models.paginations import (
    PropertyItemPagination
)

from notion_integration.api.models.common import (
    FileObject
)


class PropertyItemAbstract(ABC):

    @classmethod
    @abstractmethod
    def create_new(cls, value: str):
        """Creates a new property item
        """
        return cls()


class PropertyItem(NotionObject, PropertyItemAbstract):
    property_id: Optional[str] = idField
    property_type: Optional[str] = typeField
    next_url: Optional[str]
    notion_object = 'property_item'

    _class_map = {
        "number": "NumberPropertyItem",
        "select": "SelectPropertyItem",
        "multi_select": "MultiSelectPropertyItem",
        "status": "StatusPropertyItem",
        "date": "DatePropertyItem",
        "formula": "FormulaPropertyItem",
        "files": "FilesPropertyItem",
        "checkbox": "CheckBoxPropertyItem",
        "url": "URLPropertyItem",
        "email": "EmailPropertyItem",
        "phone_number": "PhoneNumberPropertyItem",
        "created_time": "CreatedTimePropertyItem",
        "created_by": "CreatedByPropertyItem",
        "last_edited_time": "LastEditedTimePropertyItem",
        "last_edited_by": "LastEditedByPropertyItem",
        "people": "PeoplePropertyItem"
    }

    @property
    def _class_key_field(self):
        return self.property_type

    @classmethod
    def create_new(cls, value: Dict[str, Any]):
        """Creates a new property item
        """
        return cls(**value)

    def get_dict_for_post(self):
        return {self.property_type: self.value}


class TitlePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'title'

    title: RichTextObject

    @property
    def value(self):
        return self.title.plain_text

    def set_value(self, title: str):
        """Only allowing plain text.
        Any existing rich text information will be removed.

        """
        self.title = RichTextObject.from_str(title)

    def get_dict_for_post(self):
        raise NotImplementedError(
            f"Function not yet implemented for {self.__name__}"
        )

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[
        RichTextObject, str, Tuple[str, str, Dict,
                                   Literal["text", "mention", "equation"]]
    ]):
        if isinstance(value, RichTextObject):
            return cls(title=value)
        elif isinstance(value, str):
            return cls(title=RichTextObject.from_str(value))
        else:
            return cls(title=RichTextObject(plain_text=value[0],
                                            href=value[1],
                                            annotations=value[2],
                                            type=value[3]))


class TitlePagination(PropertyItemPagination):
    _class_key_field = None

    results: List[TitlePropertyItem]


class RichTextPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "rich_text"

    rich_text: RichTextObject

    @property
    def value(self):
        return self.rich_text.plain_text

    def set_value(self, plain_text: str, href: Optional[str] = None,
                  annotations: Optional[Dict] = None,
                  rich_text_type: Literal[
                      "text", "mention", "equation"] = 'text'):
        self.rich_text = RichTextObject(plain_text=plain_text, href=href,
                                        annotations=annotations,
                                        type=rich_text_type)

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[
        RichTextObject, str, Tuple[str, str, Dict,
                                   Literal["text", "mention", "equation"]]
    ]):
        if isinstance(value, RichTextObject):
            return cls(rich_text=value)
        elif isinstance(value, str):
            return cls(rich_text=RichTextObject.from_str(value))
        else:
            return cls(rich_text=RichTextObject(
                plain_text=value[0],
                href=value[1],
                annotations=value[2],
                type=value[3]
            ))


class RichTextPagination(PropertyItemPagination):
    _class_key_field = None

    results: List[RichTextPropertyItem]


class NumberPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'number'

    number: Optional[float] = Field(...)

    @property
    def value(self):
        return self.number

    def set_value(self, value: float):
        self.number = value

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: float):
        return cls(number=value)


class SelectPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'select'

    select: Optional[SelectValue] = Field(...)

    @property
    def value(self):
        if self.select is not None:
            return self.select.name

    def set_value(self, name: str, color: Optional[str] = None,
                  select_id: Optional[str] = None):
        self.select = SelectValue(name=name, color=color, id=select_id)

    def get_dict_for_post(self):
        return {'select': {'name': self.value}}

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[str, SelectValue, Tuple[str, str],
                                     Tuple[str, str, str]]):
        if isinstance(value, SelectValue):
            return cls(select=value)
        elif isinstance(value, str):
            return cls(select=SelectValue(name=value))
        elif len(value) == 2:
            return cls(select=SelectValue(name=value[0], color=value[1]))
        else:
            return cls(select=SelectValue(name=value[0], color=value[1],
                                          id=value[2]))


class StatusPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'status'

    status: Optional[StatusValue] = Field(...)

    @property
    def value(self):
        if self.status is not None:
            return self.status.name

    def set_value(self, name: str, color: Optional[str] = None,
                  status_id: Optional[str] = None):
        self.status = StatusValue(name=name, color=color, id=status_id)

    def get_dict_for_post(self):
        """
        As of 03/08/22, the format specified on the Notion documentation
        does not seem to work.
        https://developers.notion.com/reference/property-value-object#
        status-property-values
        """
        # return {'status': {'name': self.value}}
        raise NotImplementedError(
            f"Function not yet implemented for {self.__name__}"
        )

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[str, Tuple[str, str],
                                     Tuple[str, str, str]]):
        if isinstance(value, str):
            return cls(status=StatusValue(name=value))
        elif len(value) == 2:
            return cls(status=StatusValue(name=value[0], color=value[1]))
        else:
            return cls(status=StatusValue(name=value[0], color=value[1],
                                          id=value[2]))


class MultiSelectPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'multi_select'

    multi_select: List[SelectValue]

    @property
    def value(self):
        return [so.name for so in self.multi_select]

    def set_value(self, name: str, color: Optional[str] = None):
        self.multi_select = [SelectValue(name=name, color=color)]

    def get_dict_for_post(self):
        return {"multi_select": [
            {"name": so.name} for so in self.multi_select]}

    @classmethod
    def from_simpler_inputs(cls, name: str, color: Optional[str] = None):
        return cls(multi_select=[SelectValue(name=name, color=color)])

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[str, SelectValue, Tuple[str, str],
                                     Tuple[str, str, str]]):
        if isinstance(value, SelectValue):
            return cls(multi_select=[value])
        elif isinstance(value, str):
            return cls(multi_select=[SelectValue(name=value)])
        elif len(value) == 2:
            return cls(multi_select=[SelectValue(name=value[0],
                                                 color=value[1])])
        else:
            return cls(multi_select=[SelectValue(name=value[0], color=value[1],
                                                 id=value[2])])


class DatePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'date'

    date: Optional[DatePropertyValue] = Field(...)

    @property
    def value(self):
        if self.date is not None:
            return self.date.start

    def set_value(self, start: Union[datetime, date_type],
                  end: Optional[Union[datetime, date_type]] = None,
                  time_zone: Optional[str] = None):
        self.date = DatePropertyValue(start=start, end=end,
                                      time_zone=time_zone)

    def get_dict_for_post(self):
        d = dict(start=self.date.start.isoformat())
        if self.date.end is not None:
            d['end'] = self.date.end.isoformat()
        if self.date.time_zone is not None:
            d['time_zone'] = self.date.time_zone
        return {"date": d}

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[
        DatePropertyValue, datetime, Tuple[datetime, datetime],
        Tuple[datetime, str], Tuple[datetime, datetime, str]
    ]):
        if isinstance(value, DatePropertyValue):
            return cls(date=value)
        elif isinstance(value, datetime):
            return cls(date=DatePropertyValue(start=value))
        elif len(value) == 2 and isinstance(value[1], datetime):
            return cls(date=DatePropertyValue(start=value[0], end=value[1]))
        elif len(value) == 2:
            return cls(date=DatePropertyValue(start=value[0],
                                              time_zone=value[1]))
        else:
            return cls(date=DatePropertyValue(start=value[0], end=value[1],
                                              time_zone=value[2]))


class FormulaPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'formula'

    formula: Optional[FormulaValue] = Field(...)

    @property
    def value(self):
        return getattr(self.formula, self.formula.formula_type)

    def set_value(self, formula_type: str):
        self.formula = FormulaValue(formula_type=formula_type)

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: str):
        return cls(formula=FormulaValue(formula_type=value))

    def set_value(self, formula_type: str):
        self.formula = FormulaValue(formula_type=formula_type)

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: str):
        return cls(formula=FormulaValue(formula_type=value))


class RelationPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'relation'

    relation: Optional[PageReferenceValue] = Field(...)

    @property
    def value(self):
        return self.relation.page_id

    def set_value(self, page_id: str):
        self.relation = PageReferenceValue(id=page_id)

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[PageReferenceValue, str]):      
        if isinstance(value, PageReferenceValue):
            return cls(relation=value)
        else:
            return cls(relation=PageReferenceValue(id=value))


class RelationPagination(PropertyItemPagination):
    _class_key_field = None

    results: List[RelationPropertyItem]


class RollupPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "rollup"

    rollup: RollupValue

    @property
    def value(self):
        return ''

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: RollupValue):
        return cls(rollup=value)


class RollupPagination(PropertyItemPagination):
    _class_key_field = None

    results: List

    @property
    def value(self):
        return [PropertyItem.from_obj(res).value for res in self.results]


class PeoplePropertyItem(PropertyItem):
    _class_key_field = None

    people: User

    @property
    def value(self):
        return self.people.name

    def set_value(self, **kwargs):
        self.people = User(**kwargs)

    @classmethod
    def from_simpler_inputs(cls, **kwargs):
        return cls(people=User(object='user', **kwargs))

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: Union[
        User, str,
        Tuple[str, Optional[Literal["person", "bot"]], Optional[str],
              Optional[str], Optional[Dict], Optional[str], Optional[Dict],
              Optional[Literal["workspace", "user"]]]
    ]):
        """Creates a new PeoplePropertyItem
        The User object used to construct the item can take many arguments.
        To simplify the options here, you can either provide a User object,
        the user id, or a tuple with all options in the correct order (most of
        which can be None)

        Args:
            value: User object, the user id, or a tuple (in which most entries
            can be None)

        Returns: PeoplePropertyItem

        """
        if isinstance(value, User):
            return cls(people=value)
        elif isinstance(value, str):
            return cls(people=User(object='user', id=value))
        else:
            return cls(people=User(
                object='user', id=value[0], type=value[1], name=value[2],
                avatar_url=value[3], person=value[4], person_email=value[5],
                bot=value[6], owner_type=value[7]
            ))


class PeoplePagination(PropertyItemPagination):
    _class_key_field = None

    results: List[PeoplePropertyItem]


class FilesPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "files"

    files: List[FileReferenceValue]

    @property
    def value(self):
        return [file.value for file in self.files]

    def set_value(self, reference_type: str, name: str,
                  external: Optional[FileObject], file: Optional[FileObject]):

        self.files = [FileReferenceValue(reference_type=reference_type,
                                         name=name, external=external,
                                         file=file)]

    @classmethod
    @pydantic.validate_arguments
    def create_new(
            cls,
            value: Union[FileReferenceValue,
                         Tuple[str, str, Optional[FileObject],
                               Optional[FileObject]]]
    ):
        if isinstance(value, FileReferenceValue):
            return cls(files=[value])
        else:
            return cls(files=[FileReferenceValue(
                reference_type=value[0], name=value[1],
                external=value[2], file=value[3]
            )])


class CheckBoxPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "checkbox"

    checkbox: Optional[bool] = Field(...)

    @property
    def value(self):
        return self.checkbox

    def set_value(self, checkbox: bool):
        self.checkbox = checkbox

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: bool):
        return cls(checkbox=value)


class URLPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "url"

    url: Optional[str] = Field(...)

    @property
    def value(self):
        return self.url

    def set_value(self, url: str):
        self.url = url

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: str):
        return cls(url=value)


class EmailPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "email"

    email: Optional[str] = Field(...)

    @property
    def value(self):
        return self.email

    def set_value(self, email: str):
        self.email = email

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: str):
        return cls(email=value)


class PhoneNumberPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "phone_number"

    phone_number: Optional[str] = Field(...)

    @property
    def value(self):
        return self.phone_number

    def set_value(self, phone_number: str):
        self.phone_number = phone_number

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: str):
        return cls(phone_number=value)


class CreatedTimePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "created_time"

    created_time: str

    @property
    def value(self):
        return self.created_time

    def set_value(self, created_time: str):
        self.created_time = created_time

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: str):
        return cls(created_time=value)


class CreatedByPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "created_by"

    created_by: User

    @property
    def value(self):
        return self.created_by.name

    def set_value(self, created_by: User):
        self.created_by = created_by

    @classmethod
    @pydantic.validate_arguments
    def create_new(
        cls,
        value: Union[
            User, str,
            Tuple[
                str,
                Optional[Literal["person", "bot"]],
                Optional[str],
                Optional[str],
                Optional[Dict],
                Optional[str],
                Optional[Dict],
                Optional[Literal["workspace", "user"]]]
        ]
    ):
        """Creates a new CreatedByPropertyItem
        The User object used to construct the item can take many arguments.
        To simplify the options here, you can either provide a User object,
        the user id, or a tuple with all options in the correct order (most of
        which can be None)

        Args:
            value: User object, the user id, or a tuple (in which most entries
            can be None)

        Returns: CreatedByPropertyItem

        """
        if isinstance(value, User):
            return cls(created_by=value)
        elif isinstance(value, str):
            return cls(created_by=User(object='user', id=value))
        else:
            return cls(created_by=User(
                object='user', id=value[0], type=value[1], name=value[2],
                avatar_url=value[3], person=value[4], person_email=value[5],
                bot=value[6], owner_type=value[7]
            ))


class LastEditedTimePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "last_edited_time"

    last_edited_time: str

    @property
    def value(self):
        return self.last_edited_time

    def set_value(self, last_edited_time: str):
        self.last_edited_time = last_edited_time

    @classmethod
    @pydantic.validate_arguments
    def create_new(cls, value: str):
        return cls(last_edited_time=value)


class LastEditedByPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "last_edited_by"

    last_edited_by: User

    @property
    def value(self):
        return self.last_edited_by.name

    def set_value(self, last_edited_by: User):
        self.last_edited_by = last_edited_by

    @classmethod
    @pydantic.validate_arguments
    def create_new(
            cls,
            value: Union[
                User, str,
                Tuple[
                    str, Optional[Literal["person", "bot"]], Optional[str],
                    Optional[str], Optional[Dict], Optional[str],
                    Optional[Dict],
                    Optional[Literal["workspace", "user"]]]
            ]):
        """Creates a new LastEditedByPropertyItem
        The User object used to construct the item can take many arguments.
        To simplify the options here, you can either provide a User object,
        the user id, or a tuple with all options in the correct order (most of
        which can be None)

        Args:
            value: User object, the user id, or a tuple (in which most entries
            can be None)

        Returns: LastEditedByPropertyItem

        """
        if isinstance(value, User):
            return cls(last_edited_by=value)
        elif isinstance(value, str):
            return cls(last_edited_by=User(object='user', id=value))
        else:
            return cls(last_edited_by=User(
                object='user', id=value[0], type=value[1], name=value[2],
                avatar_url=value[3], person=value[4],
                person_email=value[5],
                bot=value[6], owner_type=value[7]
            ))
