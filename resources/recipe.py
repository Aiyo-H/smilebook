from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus

from webargs import fields
from webargs.flaskparser import use_kwargs

from marshmallow import ValidationError

from models.recipe import Recipe
from schemas.recipe import RecipeSchema, RecipePaginationSchema

from utils import save_image, clear_cache
from extensions import image_set, cache, limiter

import os

recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)
recipe_cover_schema = RecipeSchema(only=('cover_url', ))
recipe_pagination_schema = RecipePaginationSchema()


class RecipeListResource(Resource):
    decorators = [limiter.limit('2 per minute', methods=['GET'], error_message='Too Many Requests')]
    @use_kwargs({'q': fields.Str(missing=''),
                 'page': fields.Int(missing=1),
                 'per_page': fields.Int(missing=20),
                 'sort': fields.Str(missing='created_at'),
                 'order': fields.Str(missing='desc')}, location='query')
    @cache.cached(timeout=60, query_string=True)
    def get(self, q, page, per_page, sort, order):

        if sort not in ['created_at', 'cook_time', 'num_of_servings']:
            sort = 'created_at'

        if order not in ['asc', 'desc']:
            order = 'desc'

        paginated_recipes = Recipe.get_all_published(q, page, per_page, sort, order)

        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK

    @jwt_required()
    def post(self):
        json_data = request.get_json()

        current_user = get_jwt_identity()

        # old data, error = recipe_schema.load(data=json_data)
        try:
            data = recipe_schema.load(data=json_data)
            # Proceed with using 'data'
        except ValidationError as err:
            # Handle the validation errors, e.g., return them in the response
            return {'message': 'Validation errors', 'errors': err}, HTTPStatus.BAD_REQUEST

        # initialize the instance
        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()

        return recipe_schema.dump(recipe), HTTPStatus.CREATED


class RecipeResource(Resource):

    @jwt_required(optional=True)
    def get(self, recipe_id):

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if recipe.is_publish == False and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        res = recipe_schema.dump(recipe)
        print(res)
        return res, HTTPStatus.OK

    @jwt_required()
    def patch(self, recipe_id):

        json_data = request.get_json()

        try:
            data = recipe_schema.load(data=json_data, partial=('name',))
        except ValidationError as err:
            return {'message': 'Validation errors', 'errors': err.messages}, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        # check identity
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.ingredients = data.get('ingredients') or recipe.ingredients
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions

        recipe.save()

        clear_cache('/recipes')
        # do not use recipe_schema.dump(recipe).data
        return recipe_schema.dump(recipe), HTTPStatus.OK

    @jwt_required()
    def delete(self, recipe_id):

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.delete()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT


class RecipePublishResource(Resource):

    @jwt_required()
    def put(self, recipe_id):

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = True
        recipe.save()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT

    @jwt_required()
    def delete(self, recipe_id):

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = False
        recipe.save()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT


class RecipeCoverUploadResource(Resource):
    '''
    @jwt_required
    def put(self):
        print('UserAvatarUploadResource endpoint reached')
        return {'message': 'Endpoint reached'}, HTTPStatus.OK
    '''

    @jwt_required()
    def put(self, recipe_id):
        print('just started')
        file = request.files.get('cover')

        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        # check file extension/type
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        if recipe.cover_image:
            cover_path = image_set.path(folder='covers', filename=recipe.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)

        filename = save_image(image=file, folder='covers')

        recipe.cover_image = filename

        recipe.save()
        clear_cache('/recipes')
        return recipe_cover_schema.dump(recipe), HTTPStatus.OK
