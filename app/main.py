from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse,ORJSONResponse
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func,select
from app.db import engine, get_session
from app.models import Base, SensorReading
from app.schemas import ReadingIn, Status, ErrorResponse
from app.validation import is_valid_reading
from typing import Annotated

app = FastAPI(title="IoT Stream Validator")

# Create tables on startup (simple approach for beginners)
Base.metadata.create_all(bind=engine)

class IdNotFoundError(Exception):
    
    def __str__(self):
        return "Requested id not found in the database"
    
@app.exception_handler(IdNotFoundError)
async def not_found_handler(request: Request, exc: IdNotFoundError):
    payload = ErrorResponse(code="NOT_FOUND", message=str(exc))
    return JSONResponse(status_code=404, content=payload.model_dump())

@app.get("/", tags=["meta"])
def health():
    return {"status": "online"}

@app.post("/ingest", response_model=None, status_code=status.HTTP_201_CREATED, tags=["ingest"], summary="Ingest data into the database following the schema")
def ingest(reading: ReadingIn, session: Session = Depends(get_session)):
    # Pydantic has already validated types/ranges
    ok, reason = is_valid_reading(reading)
    if not ok:
        raise HTTPException(status_code=422, detail=f"Invalid reading: {reason}")

    row = SensorReading(
        sensor_id=reading.sensor_id,
        ts=reading.ts,  # None allowed -> DB default NOW()
        temperature_c=reading.temperature_c,
        humidity_pct=reading.humidity_pct,
        status=reading.status,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return JSONResponse(status_code=201, content="Successfully ingested reading")

@app.get("/readings", response_model=None, tags=["query"], summary="Get the entire readings with default limit 50 and offset 0")
def list_readings(
    offset: int = 0, 
    limit: int = 50,
    sensor_id: str | None = None,
    status: Status | None = None,
    min_temp: float | None = None,
    max_temp: float | None = None,
    session: Session = Depends(get_session)
    ):
    if min_temp is not None and max_temp is not None and min_temp > max_temp:
        raise HTTPException(status_code=400, detail="Error: Minimum temperature cannot be greater than maximum temperature")
    rows = session.query(SensorReading)
    if sensor_id:
        rows = rows.filter(SensorReading.sensor_id == sensor_id)
    if status:
        rows = rows.filter(SensorReading.status == status)
    if min_temp:
        rows = rows.filter(SensorReading.temperature_c >= min_temp)
    if max_temp:
        rows = rows.filter(SensorReading.temperature_c <= max_temp)
    
    res = (
        rows.order_by(SensorReading.id.desc())
         .offset(offset)
         .limit(min(limit, 200))
         .all()
    )

    
    payload = [
        {
            "id": r.id,
            "sensor_id": r.sensor_id,
            "ts": r.ts,
            "temperature_c": r.temperature_c,
            "humidity_pct": r.humidity_pct,
            "status": r.status,
        }
        for r in res
    ]

    # Return a single JSONResponse with the list as content
    return JSONResponse(status_code=200, content=jsonable_encoder(payload))



@app.get("/readings/{id}", response_model=None, tags=["query"], summary="Get the readings of a particular id")
async def get_data_by_id(id: int, session: Session = Depends(get_session)):
    try:
        row = session.query(SensorReading).filter_by(id=id).one()
        return JSONResponse(
            status_code=201,
            content=jsonable_encoder(
                {
                    "id": row.id,
                    "sensor_id": row.sensor_id,
                    "ts": row.ts,
                    "temperature_c": row.temperature_c,
                    "humidity_pct": row.humidity_pct,
                    "status": row.status
                }
            )
        )
    except Exception as e:
        # row_count = session.query(SensorReading).count()
        raise IdNotFoundError()
    
@app.delete("/readings/delete/{id}", tags=["delete"], summary="Delete a record in the database by its primary key")
async def delete_data(id: int, session: Session = Depends(get_session)):
    try:
        row = session.query(SensorReading).filter_by(id=id).one()
        session.delete(row)
        session.commit()
        return f"Record with id: {id} successfully deleted from the database"
    except Exception as e:
        raise IdNotFoundError()
    
@app.get("/summary", tags=["summary", "query"], summary="Get an overview of the data distribution: max,min and average values")
async def get_summary(session: Session = Depends(get_session)):
    total_count = session.query(SensorReading).count()
    avg_temp = session.execute(select(func.avg(SensorReading.temperature_c))).scalar()
    avg_hum = session.execute(select(func.avg(SensorReading.humidity_pct))).scalar()
    max_temp = session.execute(select(func.max(SensorReading.temperature_c))).scalar()
    min_temp = session.execute(select(func.min(SensorReading.temperature_c))).scalar()
    max_hum = session.execute(select(func.max(SensorReading.humidity_pct))).scalar()
    min_hum = session.execute(select(func.min(SensorReading.humidity_pct))).scalar()
    
    return {
        "Total Count" : total_count,
        "Average Temperature": round(avg_temp,2),
        "Average Humidity": round(avg_hum,2),
        "Max Temperature": max_temp,
        "Min Temperature": min_temp,
        "Max Humidity": max_hum,
        "Min Humidity": min_hum
    }