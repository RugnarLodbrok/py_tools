from typing import TypeVar, Generic, Iterator, Type
from abc import ABC, abstractmethod


class BaseSchema:
    pass


class Schema1(BaseSchema):
    pass


class Schema2(BaseSchema):
    pass


class Schema3(BaseSchema):
    pass


T = TypeVar('T', bound=BaseSchema)


class BaseMessage(Generic[T]):
    pass


class Message1(BaseMessage[Schema1]):
    pass


class Message2(BaseMessage[Schema2]):
    pass


class Message3(BaseMessage[Schema3]):
    pass


class Message3_1(BaseMessage[Schema3]):
    pass


class BaseHandler(Generic[T], ABC):
    message_cls: Type[BaseMessage[T]]

    @abstractmethod
    def get_messages(self, event: T) -> Iterator[BaseMessage[T]]:
        pass


class Handler1(BaseHandler[Schema1]):
    message_cls = Message1

    def get_messages(self, event: Schema1) -> Iterator[Message1]:
        yield Message1()


class Handler2(BaseHandler[Schema2 | Schema3]):
    def get_messages(self, event: Schema2 | Schema3) -> Iterator[Message2 | Message3]:
        yield Message2()
        yield Message3()


class Handler3(BaseHandler[Schema3]):
    message_cls = Message3

    def get_messages(self, event: Schema3) -> Iterator[BaseMessage[Schema3]]:
        yield Message3()
        yield Message3_1()
