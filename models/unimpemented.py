# class NotionProperty(BaseModel):
#     id: str
#     type: Optional[str]
#     value: Literal[
#         "rich_text", "number", "select", "multi_select",
#         "status", "date", "formula", "relation", "rollup",
#         "title", "people", "files", "checkbox",
#         "url", "email", "phone_number", "created_time",
#         "created_by", "last_edited_time", "last_edited_by"
#     ]


# class LinkObject(BaseModel):
#     type: Literal["url"]
#     url: str


# class TextObject(BaseModel):
#     content: str
#     link: Optinal[LinkObject]

# class TemplateMentionObject(BaseModel):


# class MentionObject(BaseModel):
#     type: Literal["user", "page", "database", "date", "link_preview"]
#     user: Optional[UserObject]
#     page: Optional[PageReference]
#     database: Optional[DatabaseReference]
#     date: DatePropertyValueObject

# class RichTextObject(BaseModel):