from __future__ import annotations

import inspect
import typing

import pydantic as pd

from py_tools.common import AnyDict

SHAPE_LOOKUP = {
    pd.fields.SHAPE_LIST: list,
    pd.fields.SHAPE_SET: set,
    pd.fields.SHAPE_TUPLE: tuple,
    pd.fields.SHAPE_TUPLE_ELLIPSIS: tuple,
    pd.fields.SHAPE_SEQUENCE: typing.Sequence,
    pd.fields.SHAPE_FROZENSET: frozenset,
    pd.fields.SHAPE_ITERABLE: typing.Iterable,
    pd.fields.SHAPE_DICT: dict,
    pd.fields.SHAPE_DEFAULTDICT: typing.DefaultDict,
}


class MakeOptional(pd.main.ModelMetaclass):
    def __new__(
        mcs, name: str, bases: tuple[type, ...], namespace: AnyDict  # noqa: N804
    ) -> MakeOptional:
        if len(bases) > 1:
            raise NotImplementedError(
                "`MakeOptional` can't work with more then one base class"
            )
        if not bases or not issubclass(bases[0], pd.BaseModel):
            raise TypeError('Must be inherited from pydantic.BaseModel')

        annotations: dict[str, object] = {}

        for base in reversed(inspect.getmro(bases[0])):
            if not issubclass(base, pd.BaseModel):
                continue
            for field_name, field_type in getattr(base, '__annotations__', {}).items():
                field_info = base.__fields__.get(field_name)
                if field_info:
                    field_type = mcs._resolve_field_type(field_info)
                annotations[field_name] = field_type
        annotations.update(namespace.get('__annotations__', {}))

        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = typing.Optional[annotations[field]]
        namespace['__annotations__'] = annotations
        return super().__new__(mcs, name, bases, namespace)

    @staticmethod
    def _resolve_field_type(
        field_info: pd.fields.ModelField,
    ) -> typing.Type[typing.Any]:
        field_type = field_info.type_
        if field_info.shape in {pd.fields.SHAPE_DICT, pd.fields.SHAPE_DEFAULTDICT}:
            if not field_info.key_field:
                raise TypeError('dict-field should have key_field')  # pragma: no cover
            return SHAPE_LOOKUP[field_info.shape][  # type: ignore
                field_info.key_field.type_, field_type
            ]
        if field_info.shape == pd.fields.SHAPE_TUPLE_ELLIPSIS:
            return typing.Tuple[field_type, ...]  # type: ignore
        if field_info.shape not in {pd.fields.SHAPE_SINGLETON, pd.fields.SHAPE_TUPLE}:
            return SHAPE_LOOKUP[field_info.shape][field_type]  # type: ignore
        return field_type
