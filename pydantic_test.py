from pydantic import BaseModel


def constructor(fn):
    breakpoint()


class TestModel(BaseModel):
    foo: str

    @constructor
    def int_constructor(self, value: int):
        self.foo = value


if __name__ == '__main__':
    tm = TestModel()