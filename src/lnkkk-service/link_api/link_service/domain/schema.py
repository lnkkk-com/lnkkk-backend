from marshmallow import Schema, fields


class LinkSchema(Schema):
    id = fields.Str()
    title = fields.Str()
    href = fields.Str()
