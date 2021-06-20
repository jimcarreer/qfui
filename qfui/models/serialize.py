import enum
import json
import typing
from dataclasses import asdict, is_dataclass
from typing import Union


class SerializationError(Exception):
    pass


class Serializer:

    __TERMINAL_TYPES__ = [str, int, float, bool]

    @classmethod
    def serialize_value(cls, value, _visited: typing.Optional[set] = None):
        if any(isinstance(value, t) for t in cls.__TERMINAL_TYPES__) or value is None:
            return value
        if issubclass(value.__class__, enum.Enum):
            return cls.serialize_value(value.value)
        _visited = _visited or set()
        if id(value) in _visited:
            raise SerializationError(f"Circular reference detected for {repr(value)}")
        _visited.add(id(value))
        if isinstance(value, dict):
            ret = cls.serialize_dict(value)
        elif isinstance(value, list):
            ret = [cls.serialize_value(v, _visited) for v in value]
        elif is_dataclass(value):
            ret = cls.serialize_dict(asdict(value))
        else:
            raise SerializationError(f"Could not serialize {repr(value)} (type: {type(value)}")
        _visited.remove(id(value))
        return ret

    @classmethod
    def serialize_key(cls, key) -> str:
        ret = cls.serialize_value(key)
        if isinstance(ret, str):
            return ret
        error = f"Dictionary key {repr(key)} is not a string (it is: {type(key)}) nor does it serialize to a string."
        raise SerializationError(error)

    @classmethod
    def serialize_dict(cls, target: dict) -> Union[dict, list, int, str, float, bool]:
        return {cls.serialize_key(k): cls.serialize_value(v) for k, v in target.items()}


class SerializingJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return Serializer.serialize_value(o)
        return super().default(o)
