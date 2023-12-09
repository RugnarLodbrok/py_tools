"""
Хочу посоветоваться про организацию конфига в support-bot. В сервисе много консьюмеров (7 штук),
поэтому есть мотивация использовать вложенные сущности Settings. Детали в треде.

Сразу пример:
```
# по-старому
class KaasConfig:
    ...
    MESSAGES_TOPIC: str
    MESSAGES_CONSUMER_GROUP: str
    EVENTS_TOPIC: str
    EVENTS_CONSUMER_GROUP: str
    DEDUPLICATION_TOPIC: str
    DEDUPLICATION_CONSUMER_GROUP: str
    ...

    class Config:
        env_prefix = 'KAAS_'

```

```
# nested
class Consumer(BaseSettings):
    TOPIC: str
    CONSUMER_GROUP: str


class KaasConfig:
    ...
    MESSAGES: Consumer
    EVENTS: Consumer
    DEDUPLICATION: Consumer
    ...

    class Config:
        env_prefix = 'KAAS_'
        env_nested_delimiter = '__'  # (1)
        case_sensitive = True  # (2)
```

Когда сделал, нашел пару неудобств (в коде отмечены комментами 1 и 2).
1. env_nested_delimiter приходится делать отличным от `'_'`, иначе криво парсится. Тогда переменные окружения будут вида
`KAAS_MESSAGES__TOPIC`. Не уверен что это красиво.
2. Пришлось добавить `case_sensitive = True`. Если не добавлять то вложенную модель надо делать в lowercase.
```
class Consumer(BaseSettings):
    topic: str
    consumer_group: str
```
У кого-нибудь есть идеи, стоит вложенные settings использовать или пусть лучше просто плоская структура будет?
"""
import os

from pydantic import BaseSettings


# example2
class KaasConfig:
    ...
    MESSAGES_TOPIC: str
    MESSAGES_CONSUMER_GROUP: str
    EVENTS_TOPIC: str
    EVENTS_CONSUMER_GROUP: str
    DEDUPLICATION_TOPIC: str
    DEDUPLICATION_CONSUMER_GROUP: str

    class Config:
        env_prefix = 'KAAS_'


# example1
class Consumer(BaseSettings):
    topic: str
    consumer_group: str


class KaasConfig:
    ...
    MESSAGES: Consumer
    EVENTS: Consumer
    DEDUPLICATION: Consumer

    class Config:
        env_prefix = 'KAAS_'
        env_nested_delimiter = '__'
        case_sensitive = True


# -----


class Item(BaseSettings):
    C: str
    D: str


class Settings(BaseSettings):
    A: str
    B: Item

    class Config:
        env_prefix = 'KAAS_'
        env_nested_delimiter = '_'
        case_sensitive = True


if __name__ == '__main__':
    os.environ['KAAS_A'] = '123'
    os.environ['KAAS_B_C'] = '123'
    os.environ['KAAS_B_D'] = '123'
    Settings()
