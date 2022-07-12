from pydantic import BaseModel
from typing import Union, ClassVar


class B(BaseModel):
    _c: ClassVar[str] = 'foo'


class C(B):
    _c = 'bar'
    bar: str


typeBC = Union[B, C]

if __name__ == '__main__':
    print(B._c)
    print(C._c)
