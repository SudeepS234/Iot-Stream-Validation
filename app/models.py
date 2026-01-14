from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, DateTime, func

class Base(DeclarativeBase):
    pass

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[str] = mapped_column(String(64), index=True)
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    temperature_c: Mapped[float] = mapped_column(Float)
    humidity_pct: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16), index=True)
