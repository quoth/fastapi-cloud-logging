import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest

from fastapi_cloud_logging.utils import serialize_json


@dataclass
class DataObject:
    id: str
    created_at: datetime


@pytest.mark.parametrize(
    "object, expected",
    [
        ("str", '"str"'),
        (datetime(2021, 9, 12, 2, 1), '"2021-09-12T02:01:00"'),
        (["a", "b"], '["a", "b"]'),
        ({"id": "id123", "name": "John Doe"}, '{"id": "id123", "name": "John Doe"}'),
        (
            {"sign_in_at": datetime(2022, 6, 12, 22, 33)},
            '{"sign_in_at": "2022-06-12T22:33:00"}',
        ),
        (
            DataObject(id="id123", created_at=datetime(2022, 6, 9, 22, 33)),
            '{"id": "id123", "created_at": "2022-06-09T22:33:00"}',
        ),
    ],
)
def test_serialize_json(object: Any, expected: str):
    assert json.dumps(object, default=serialize_json) == expected
