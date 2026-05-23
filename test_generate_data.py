import pytest
import generate_data
import csv

from datetime import datetime

@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        (datetime(2026, 4, 6, 8, 0), True),
        (datetime(2026, 4, 6, 17, 59), True),
        (datetime(2026, 4, 6, 18, 0), False),
        (datetime(2026, 4, 4, 10, 0), False),
    ],
)

def test_is_working_houts_identifies_business_hours(timestamp, expected):
    result = generate_data.is_working_hours(timestamp)
    assert result == expected

@pytest.mark.parametrize(
    ("equipment_id", "equipment_type"),
    [
        ("AHU_01", "AHU"),
        ("FCU_01", "FCU"),
        ("PUMP_01", "PUMP"),
        ("CHILLER_01", "CHILLER"),
    ]
)

def test_generate_alarm_returns_only_valid_alarm_for_equipment(
    monkeypatch,
    equipment_id,
    equipment_type,
):
    monkeypatch.setattr(generate_data.random, "random", lambda: 0.0)

    alarm_type = generate_data.generate_alarm(equipment_id, equipment_type)

    assert alarm_type in generate_data.ALARM_TYPES_BY_EQUIPMENT[equipment_type]
