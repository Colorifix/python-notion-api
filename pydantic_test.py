from pydantic import BaseModel
from typing import Dict


class FooBase(BaseModel):
    pass


class Foo(FooBase):
    foo: str


class Bar(BaseModel):
    bar: Dict[str, FooBase]


if __name__ == '__main__':
    foo = Foo(foo='foo')
    bar = Bar(bar={'foo': foo})

    print(bar.json())
