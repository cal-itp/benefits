import logging
from dataclasses import dataclass

from benefits.enrollment.api import BaseDataClass


class TestBaseDataClass:

    @dataclass
    class SampleDataClass(BaseDataClass):
        fieldOne: int
        fieldTwo: str

    def test_from_kwargs(self, caplog):
        response_json = {"fieldOne": 1, "fieldTwo": "two", "fieldThree": "three"}

        with caplog.at_level(logging.DEBUG):
            instance = self.SampleDataClass.from_kwargs(**response_json)

        assert instance.fieldOne == 1
        assert instance.fieldTwo == "two"
        assert f"Unexpected arg parsing response for {self.SampleDataClass}: fieldThree = three" in caplog.text
