from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api
from flask_uploads import configure_uploads

import json
from config import Config
from extensions import db, jwt, image_set, cache, limiter

from resources.user import UserListResource, UserResource, MeResource, UserRecipeListResource, UserActivateResource, UserAvatarUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource, RecipeCoverUploadResource
import os
import logging


def create_app():

    env = os.environ.get('ENV', 'Development')

    if env == 'Production':
        config_str = 'config.ProductionConfig'
    elif env == 'Staging':
        config_str = 'config.StagingConfig'
    else:
        config_str = 'config.DevelopmentConfig'

    # original
    app = Flask(__name__)
    app.config.from_object(config_str)

    register_extensions(app)
    register_resources(app)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    configure_uploads(app, image_set)
    # patch_request_class is in flask-uploads but removed in flask-reupload
    # patch_request_class(app, 10 * 1024 * 1024)

    # Set the maximum content length for incoming requests
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit
    cache.init_app(app)
    limiter.init_app(app)

    # change from jwt.token_in_blacklist_loader to jwt.token_in_blocklist_loader()
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in black_list

    @limiter.request_filter
    def ip_whitelist():
        # the local host
        return request.remote_addr == '127.0.0.1'
    '''
    #for testing
    @app.before_request
    def before_request():
        print('\n==================== BEFORE REQUEST ====================\n')
        print(cache.cache._cache.keys())
        print('\n=======================================================\n')

    @app.after_request
    def after_request(response):
        print('\n==================== AFTER REQUEST ====================\n')
        print(cache.cache._cache.keys())
        print(cache.cache._cache.items())
        print('\n=======================================================\n')
        return response
    '''


def register_resources(app):
    api = Api(app)

    api.add_resource(UserListResource, '/users')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')

    api.add_resource(MeResource, '/me')

    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')

    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
    api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')
    api.add_resource(RecipeCoverUploadResource, '/recipes/cover/<int:recipe_id>')


if __name__ == '__main__':
    app = create_app()
    app.run()


