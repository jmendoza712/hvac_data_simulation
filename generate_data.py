import csv
import random
from datetime import datetime, timedelta

SITE_ID = 'LONDON_SITE_01'
BUILDING_ID = 'BUILDING_01'

EQUIPMENT = [
    {'equipment_id': 'AHU_01', 'equipment_type': 'AHU', 'floor_id': 'FLOOR_01'},
    {'equipment_id': 'AHU_02', 'equipment_type': 'AHU', 'floor_id': 'FLOOR_03'},
    {'equipment_id': 'FCU_01', 'equipment_type': 'FCU', 'floor_id': 'FLOOR_01'},
    {'equipment_id': 'FCU_02', 'equipment_type': 'FCU', 'floor_id': 'FLOOR_02'},
    {'equipment_id': 'PUMP_01', 'equipment_type': 'PUMP', 'floor_id': 'FLOOR_00'},
    {'equipment_id': 'CHILLER_01', 'equipment_type': 'CHILLER', 'floor_id': 'FLOOR_00'},
]

ALARM_TYPES_BY_EQUIPMENT = {
    "AHU": ["HIGH_TEMPERATURE", "LOW_PRESSURE", "HIGH_CO2", "EQUIPMENT_OFF_DURING_WORKING_HOURS"],
    "FCU": ["HIGH_TEMPERATURE", "EQUIPMENT_OFF_DURING_WORKING_HOURS"],
    "PUMP": ["LOW_PRESSURE", "EQUIPMENT_OFF_DURING_WORKING_HOURS"],
    "CHILLER": ["HIGH_TEMPERATURE", "LOW_PRESSURE", "EQUIPMENT_OFF_DURING_WORKING_HOURS"],
}

OUTPUT_FILE = 'equipment_data.csv'

def is_working_hours(timestamp: datetime) -> bool:
    """Return True if timestamp is Monday-Friday, 08:00-18:00."""
    is_weekday = timestamp.weekday() < 5  # 0-4 are Monday-Friday
    is_working_time = 8 <= timestamp.hour < 18
    return is_weekday and is_working_time

def generate_alarm(equipment_id: str, equipment_type: str) -> str | None:
    """
    Generate occasional anomalies.
    AHU_02 has a higher probability of recurring faults.
    """
    base_probability = 0.05 # 5% chance of an alarm

    if equipment_id == 'AHU_02':
        base_probability = 0.12 # 12% chance for AHU_02

    if random.random() > base_probability:
        return None

    valid_alarm_types = ALARM_TYPES_BY_EQUIPMENT[equipment_type]

    return random.choice(valid_alarm_types)

def generate_reading(timestamp:datetime, equipment: dict) -> dict:
    equipment_id = equipment['equipment_id']
    equipment_type = equipment['equipment_type']
    working_hours = is_working_hours(timestamp)

    alarm_type = generate_alarm(equipment_id, equipment_type)
    alarm_flag = alarm_type is not None

    equipment_status = 'ON' if working_hours else random.choices(['ON', 'OFF'])

    if alarm_type == 'EQUIPMENT_OFF_DURING_WORKING_HOURS':
        equipment_status = 'OFF'

    temperature_c = None
    humidity_pct = None
    pressure_pa = None
    co2_ppm = None

    if equipment_type in ['AHU', 'FCU']:
        temperature_c = round(random.uniform(20.0, 24.0), 2)
        humidity_pct = round(random.uniform(40.0, 60.0), 2)

        if working_hours:
            temperature_c += round(random.uniform(0.5, 1.5), 2)  # Slightly higher during working hours

    if equipment_type == 'AHU':
        pressure_pa = round(random.uniform(95.0, 110.0), 2)
        co2_ppm = random.randint(600, 900) if working_hours else random.randint(400, 600)

    if equipment_type == 'FCU':
        pressure_pa = round(random.uniform(80.0, 100.0), 2)
        co2_ppm = None

    if equipment_type == 'PUMP':
        pressure_pa = round(random.uniform(120.0, 160.0), 2)

    if equipment_type == 'CHILLER':
        temperature_c = round(random.uniform(6.0, 12.0), 2)
        pressure_pa = round(random.uniform(130.0, 180.0), 2)

    # Apply anomalies
    if alarm_type == 'HIGH_TEMPERATURE' and temperature_c is not None:
        temperature_c = round(random.uniform(27.0, 32.0), 2)

    if alarm_type == 'LOW_TEMPERATURE' and temperature_c is not None:
        temperature_c = round(random.uniform(15.0, 19.0), 2)

    if alarm_type == 'HIGH_PRESSURE' and pressure_pa is not None:
        pressure_pa = round(random.uniform(110.0, 140.0), 2)

    if alarm_type == 'LOW_PRESSURE' and pressure_pa is not None:
        pressure_pa = round(random.uniform(60.0, 85.0), 2)

    if alarm_type == 'HIGH_CO2' and co2_ppm is not None:
        co2_ppm = random.randint(1100, 1800)

    return {
        'timestamp': timestamp.isoformat(),
        'site_id': SITE_ID,
        'building_id': BUILDING_ID,
        'floor_id': equipment['floor_id'],
        'equipment_id': equipment_id,
        'equipment_type': equipment_type,
        'temperature_c': temperature_c,
        'humidity_pct': humidity_pct,
        'pressure_pa': pressure_pa,
        'co2_ppm': co2_ppm,
        'equipment_status': equipment_status,
        'alarm_flag': alarm_flag,
        'alarm_type': alarm_type
    }

def generate_dataset(start_date: datetime, days: int = 14, interval_minutes: int = 5) -> list[dict]:
    readings = []
    current_timestamp = start_date
    end_timestamp = start_date + timedelta(days=days)

    while current_timestamp < end_timestamp:
        for equipment in EQUIPMENT:
            readings.append(generate_reading(current_timestamp, equipment))

        current_timestamp += timedelta(minutes=interval_minutes)

    return readings

def write_to_csv(readings: list[dict], output_file: str) -> None:
    fieldnames = [
        'timestamp',
        'site_id',
        'building_id',
        'floor_id',
        'equipment_id',
        'equipment_type',
        'temperature_c',
        'humidity_pct',
        'pressure_pa',
        'co2_ppm',
        'equipment_status',
        'alarm_flag',
        'alarm_type'
    ]

    with open(output_file, mode = 'w', newline = '') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(readings)

if __name__ == "__main__":
    start_date = datetime(2026, 4, 1, 0, 0)

    readings = generate_dataset(
        start_date=start_date,
        days=14,
        interval_minutes=5,
    )

    write_to_csv(readings, OUTPUT_FILE)

    print(f"Generated {len(readings)} records")
    print(f"Output file: {OUTPUT_FILE}")
