from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.parking_schema import ParkingSchema
from schema.gps_schema import GpsSchema
from domain.aggregated_data import AggregatedData

class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    parking = fields.Nested(ParkingSchema)
    time = fields.DateTime('iso')