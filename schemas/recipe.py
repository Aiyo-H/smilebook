from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from flask import url_for
from schemas.user import UserSchema
from schemas.pagination import PaginationSchema


def validate_num_of_servings(n):
    if n < 1:
        raise ValidationError('Number of servings must be greater than 0.')
    if n > 50:
        raise ValidationError('Number of servings must not be greater than 50.')


class RecipeSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    ingredients = fields.String(validate=[validate.Length(max=1000)])
    num_of_servings = fields.Integer(validate=validate_num_of_servings)
    cook_time = fields.Integer()
    directions = fields.String(validate=[validate.Length(max=1000)])
    is_publish = fields.Boolean(dump_only=True)
    cover_url = fields.Method(serialize='dump_cover_url')

    # named author here to avoid confusion and
    # declare 'user' in attribute to point out the original attribute in User schema
    # only show id and username: only=['id', 'username']
    author = fields.Nested(UserSchema, attribute='user', dump_only=True, exclude=('email',))

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    '''
    # No need to wrap multiple data records with the data key
    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data
    '''

    # another way of setting validating method
    @validates('cook_time')
    def validate_cook_time(self, value):
        if value < 1:
            raise ValidationError('Cook time must be greater than 0.')
        if value > 300:
            raise ValidationError('Cook time must not be greater than 300.')

    def dump_cover_url(self, recipe):
        if recipe.cover_image:
            return url_for('static', filename='images/covers/{}'.format(recipe.cover_image), _external=True)
        else:
            return url_for('static', filename='images/assets/default-cover.jpg', _external=True)


class RecipePaginationSchema(PaginationSchema):
    data = fields.Nested(RecipeSchema, attribute='items', many=True)