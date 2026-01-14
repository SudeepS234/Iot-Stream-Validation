from app.schemas import ReadingIn, Status

def is_valid_reading(r: ReadingIn) -> tuple[bool, str | None]:

    # Example rule: prohibit "ok" if temperature > 80 C
    if r.status == Status.ok and r.temperature_c > 80:
        return False, "status=ok not allowed above 80C"

    # Example: humidity must be <= 90 if sensor is 'HX' series
    if r.sensor_id.startswith("HX") and r.humidity_pct > 90:
        return False, "HX series humidity cannot exceed 90%"

    return True, None
