from pydantic import BaseModel, Extra, root_validator
from typing import Dict


class Foo(BaseModel):
    foo: str
    bar: str
    baz: str

    # class Config:
    #     orm_mode = True


class Bar(BaseModel, extra=Extra.ignore):
    brr: Foo

    @root_validator(pre=True)
    def validate_bar(cls, values):
        values['brr'] = values
        return values


if __name__ == '__main__':
    bar = Bar(foo='foo', bar='bar', baz='baz')
    print(bar.dict())
