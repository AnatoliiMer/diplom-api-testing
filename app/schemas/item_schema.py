from marshmallow import Schema, fields, validate, validates, ValidationError

class ItemSchema(Schema):
    """Схема для валидации товара."""
    
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="Name must be between 1 and 100 characters")
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0, error="Price must be non-negative")
    )
    description = fields.Str(allow_none=True, validate=validate.Length(max=500))
    in_stock = fields.Bool(missing=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('price')
    def validate_price(self, value):
        """Дополнительная валидация цены."""
        if value is not None and value < 0:
            raise ValidationError("Price cannot be negative")
        return value

class ItemQuerySchema(Schema):
    """Схема для query параметров (пагинация и фильтрация)."""
    
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    in_stock = fields.Bool(missing=None)
    min_price = fields.Float(missing=None, validate=validate.Range(min=0))
    max_price = fields.Float(missing=None, validate=validate.Range(min=0))