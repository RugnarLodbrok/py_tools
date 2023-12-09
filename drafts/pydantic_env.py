import os

import pytest
from pydantic import BaseSettings, Field, ValidationError


class Config(BaseSettings):
    A: str = Field(env=['PREF_A', 'A'])
    RUN_CONSUMER_IN_THREADS: bool = False
    USE_KAAS: bool = Field(False, env='USE_KAAS')

    class Config:
        env_prefix = 'KAAS_'


if __name__ == '__main__':
    with pytest.raises(ValidationError):
        Config()
    os.environ['KAAS_A'] = 'A'
    with pytest.raises(ValidationError):
        Config()
    os.environ['A'] = 'A'
    assert Config().A == 'A'
    os.environ['PREF_A'] = 'PREF_A'
    assert Config().A == 'PREF_A'

    os.environ['USE_KAAS'] = 'yes'
    assert Config().USE_KAAS
    os.environ['USE_KAAS'] = 'no'
    assert not Config().USE_KAAS

    os.environ['KAAS_USE_KAAS'] = 'no'
    assert Config().USE_KAAS
