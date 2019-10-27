from marshmallow import Schema, fields

class RequestSchema(Schema):
    token = fields.Str()
    connection_string = fields.Str()
    worker_count = fields.Int()