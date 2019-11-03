#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.
import copy
import dataclasses
import datetime
import enum
import typing
from unittest import mock

import pytest

from hikari.core.models import base


@dataclasses.dataclass()
class DummySnowflake(base.Snowflake):
    id: int


@pytest.fixture()
def neko_snowflake():
    return DummySnowflake(537340989808050216)


class DummyNamedEnum(base.NamedEnum, enum.IntEnum):
    FOO = 9
    BAR = 18
    BAZ = 27


@pytest.mark.model
class TestSnowflake:
    def test_Snowflake_init_subclass(self):
        instance = DummySnowflake(12345)
        assert instance is not None
        assert isinstance(instance, base.Snowflake)

    def test_Snowflake_comparison(self):
        assert DummySnowflake(12345) < DummySnowflake(12346)
        assert not (DummySnowflake(12345) < DummySnowflake(12345))
        assert not (DummySnowflake(12345) < DummySnowflake(12344))

        assert DummySnowflake(12345) <= DummySnowflake(12345)
        assert DummySnowflake(12345) <= DummySnowflake(12346)
        assert not (DummySnowflake(12346) <= DummySnowflake(12345))

        assert DummySnowflake(12347) > DummySnowflake(12346)
        assert not (DummySnowflake(12344) > DummySnowflake(12345))
        assert not (DummySnowflake(12345) > DummySnowflake(12345))

        assert DummySnowflake(12345) >= DummySnowflake(12345)
        assert DummySnowflake(12347) >= DummySnowflake(12346)
        assert not (DummySnowflake(12346) >= DummySnowflake(12347))

    @pytest.mark.parametrize("operator", [getattr(DummySnowflake, o) for o in ["__lt__", "__gt__", "__le__", "__ge__"]])
    def test_Snowflake_comparison_TypeError_cases(self, operator):
        try:
            operator(DummySnowflake(12345), object())
        except TypeError:
            pass
        else:
            assert False, f"No type error raised for bad comparison for {operator.__name__}"

    def test_Snowflake_created_at(self, neko_snowflake):
        assert neko_snowflake.created_at == datetime.datetime(2019, 1, 22, 18, 41, 15, 283_000).replace(
            tzinfo=datetime.timezone.utc
        )

    def test_Snowflake_increment(self, neko_snowflake):
        assert neko_snowflake.increment == 40

    def test_Snowflake_internal_process_id(self, neko_snowflake):
        assert neko_snowflake.internal_process_id == 0

    def test_Snowflake_internal_worker_id(self, neko_snowflake):
        assert neko_snowflake.internal_worker_id == 2


@pytest.mark.model
def test_NamedEnumMixin_from_discord_name():
    assert DummyNamedEnum.from_discord_name("bar") == DummyNamedEnum.BAR


@pytest.mark.model
@pytest.mark.parametrize("cast", [str, repr], ids=lambda it: it.__qualname__)
def test_NamedEnumMixin_str_and_repr(cast):
    assert cast(DummyNamedEnum.BAZ) == "BAZ"


@pytest.mark.model
def test_no_hash_is_applied_to_dataclass_without_id():
    @dataclasses.dataclass()
    class NonIDDataClass:
        foo: int
        bar: float
        baz: str
        bork: object

    first = NonIDDataClass(10, 10.5, "11.0", object())
    second = NonIDDataClass(10, 10.9, "11.5", object())

    try:
        assert hash(first) != hash(second)
        assert False
    except TypeError as ex:
        assert "unhashable type" in str(ex)


@pytest.mark.model
def test_dataclass_does_not_overwrite_existing_hash_if_explicitly_defined():
    class Base:
        def __hash__(self):
            return 69

    @dataclasses.dataclass()
    class Impl(Base):
        def __hash__(self):
            return 70

    i = Impl()

    assert hash(i) == 70


@pytest.mark.model
def test_Volatile_clone_shallow():
    @dataclasses.dataclass()
    class Test(base.HikariModel):
        data: typing.List[int]
        whatever: object

        def __eq__(self, other):
            return self.data == other.data

    data = [1, 2, 3, object(), object()]
    whatever = object()
    test = Test(data, whatever)

    assert copy.copy(test) is not test
    assert copy.copy(test) == test
    assert copy.copy(test).data is not data
    assert copy.copy(test).data == data

    assert copy.copy(test).whatever is not whatever


@pytest.mark.model
def test_HikariModel_does_not_clone_ownership_fields():
    @dataclasses.dataclass()
    class Test(base.HikariModel):
        __copy_by_ref__ = ["data"]
        data: typing.List[int]

    data = [1, 2, 3]
    test = Test(data)

    assert copy.copy(test) is not test
    assert copy.copy(test).data is data


@pytest.mark.model
def test_HikariModel_does_not_clone_state_by_default_fields():
    @dataclasses.dataclass()
    class Test(base.HikariModel):
        __copy_by_ref__ = ["foo"]
        _state: typing.List[int]
        foo: int


    state = [1, 2, 3]
    foo = 12
    test = Test(state, foo)

    assert copy.copy(test) is not test
    assert copy.copy(test)._state is state


@pytest.mark.model
def test_HikariModel_copy_calls___copy__():
    @dataclasses.dataclass()
    class Test(base.HikariModel):
        pass

    t = Test()
    t._copy = mock.MagicMock()
    copy.copy(t)
    t._copy.assert_called_with(copy.copy)


@pytest.mark.model
def test_HikariModel_deepcopy_calls___deepcopy__():
    @dataclasses.dataclass()
    class Test(base.HikariModel):
        pass

    t = Test()
    t._copy = mock.MagicMock()
    copy.deepcopy(t)
    t._copy.assert_called_with(copy.deepcopy)


@pytest.mark.model
def test_HikariModel___copy_by_ref___is_inherited():
    class Base1(base.HikariModel):
        __copy_by_ref__ = ["a", "b", "c"]

    class Base2(Base1):
        __copy_by_ref__ = ["d", "e", "f"]

    class Base3(Base2):
        __copy_by_ref__ = ["g", "h", "i"]

    for letter in "abcdefghi":
        assert letter in Base3.__copy_by_ref__, f"{letter!r} was not inherited into __copy_by_ref__"
