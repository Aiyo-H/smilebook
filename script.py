from app import *
from models.user import User
from models.recipe import Recipe


# testing script
app = create_app()
with app.app_context():
    user = User(username='Jack', email='jack@email.com', password='WKQa')
    db.session.add(user)
    db.session.commit()

with app.app_context():
    milkymilk = Recipe(name='milky milk', description='This is a milk', num_of_servings=1, cook_time=10, directions='this is how you make it', user_id=1)
    db.session.add(milkymilk)
    db.session.commit()

with app.app_context():
    user = User.query.filter_by(username='Jack').first()
    print(user.recipes)

with app.app_context():
    user = User.query.filter_by(username='Aiyo').first()
    cha = Recipe(name='chahann', description='This is a chanhan', num_of_servings=1, cook_time=20, directions='this is how you make it', user_id=user.id)
    db.session.add(cha)
    db.session.commit()