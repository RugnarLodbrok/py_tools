# pylint:disable=redefined-outer-name
from typing import Any, DefaultDict, Optional, Sequence, Type

import pydantic as pd
import pytest

from py_tools.optional_fields import MakeOptional

AnyDict = dict[str, Any]


@pytest.fixture()
def response_model() -> Type[pd.BaseModel]:
    class ResponseModel(pd.BaseModel):
        required: str
        optional: Optional[str]
        default_val: str = ''
        default_none: Optional[str] = None
        field_ellipsis: str = pd.Field(default=...)
        field_default: str = pd.Field(default='abc')
        field_default_factory: str = pd.Field(default_factory=str)

        constrained: int = pd.Field(ge=0)

    return ResponseModel


@pytest.fixture()
def response_model_optional(response_model) -> Type[pd.BaseModel]:
    class ResponseModelOptional(
        response_model,
        metaclass=MakeOptional,
    ):
        pass

    return ResponseModelOptional


def test_optional_fields(response_model, response_model_optional):
    none_dict = {
        'required': None,
        'optional': None,
        'default_val': None,
        'default_none': None,
        'field_ellipsis': None,
        'field_default': None,
        'field_default_factory': None,
        'constrained': None,
    }

    with pytest.raises(pd.ValidationError):
        response_model.parse_obj(none_dict)
    response_model_optional.parse_obj(none_dict)

    assert response_model_optional.parse_obj(none_dict).dict() == none_dict


def test_constrained_field(response_model_optional):
    response_model_optional()
    with pytest.raises(pd.ValidationError):
        response_model_optional(constrained=-1)


@pytest.mark.parametrize(
    ('bases', 'exc_type'),
    [
        ((), TypeError),
        ((str,), TypeError),
        ((pd.BaseModel, str), NotImplementedError),
    ],
)
def test_invalid_model_creation(bases, exc_type):
    with pytest.raises(exc_type):
        # pylint:disable=unused-variable
        class A(*bases, metaclass=MakeOptional):  # type:ignore[misc]
            pass


def test_magic_annotation_omitted():
    class A(pd.BaseModel):
        __magic__: str
        field: str

    class B(A, metaclass=MakeOptional):
        pass

    assert B.__annotations__ == {
        '__magic__': str,
        'field': Optional[str],
    }


@pytest.mark.parametrize(
    ('container_type', 'value'),
    [
        (list[str], ['abc']),
        (set[str], {'abc'}),
        (tuple[str, int], ('abc', 123)),
        (tuple[str, ...], ('abc', 'def')),
        (Sequence[str], ['abc']),
        (frozenset[str], frozenset(['abc'])),
        (dict[str, int], {'abc': 123}),
        (DefaultDict[str, int], {'abc': 123}),
    ],
)
def test_container_fields(container_type, value):
    class A(pd.BaseModel):
        x: container_type  # type:ignore[valid-type]

    class B(A, metaclass=MakeOptional):
        pass

    assert B(x=value).x == value
    assert B().x is None  # type:ignore[call-arg]
