from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.parking_schema import ParkingSchema
from schema.gps_schema import GpsSchema


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    parking = fields.Nested(ParkingSchema)
    timestamp = fields.DateTime("iso")
    user_id = fields.String()
