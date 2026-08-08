"""
Vehicle Telemetry & IoT Breadcrumb SQLAlchemy Model.
Stores raw GPS and OBD-II telemetry streams for fleet tracking, playback, and safety analytics.
"""
from sqlalchemy import Column, String, Numeric, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class VehicleTelemetryLog(Base):
    __tablename__ = "vehicle_telemetry_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True, index=True)

    # GPS Coordinates & Physics
    latitude = Column(Numeric(10, 6), nullable=False)
    longitude = Column(Numeric(10, 6), nullable=False)
    altitude_m = Column(Float, nullable=True, default=0.0)
    speed_kmh = Column(Float, nullable=False, default=0.0)
    heading = Column(Float, nullable=True, default=0.0)  # 0 to 360 degrees
    accuracy_m = Column(Float, nullable=True, default=5.0)

    # OBD-II & Vehicle Sensor Telemetry
    ignition = Column(Boolean, nullable=False, default=True)
    fuel_level_percent = Column(Float, nullable=True)
    engine_temp_c = Column(Float, nullable=True)
    battery_voltage = Column(Float, nullable=True)
    odometer_km = Column(Numeric(12, 2), nullable=True)
    engine_rpm = Column(Float, nullable=True)

    # Sensor Raw JSON (e.g. DTC fault codes, tire pressure, G-force)
    diagnostics = Column(JSONB, nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index('ix_telemetry_vehicle_timestamp', 'vehicle_id', 'timestamp'),
        Index('ix_telemetry_trip_timestamp', 'trip_id', 'timestamp'),
    )

    def __repr__(self) -> str:
        return f"<VehicleTelemetryLog(vehicle={self.vehicle_id}, lat={self.latitude}, lng={self.longitude}, speed={self.speed_kmh}km/h)>"
