from faker import Faker
from app import app, db
from models import User, Recipe
from random import choice

fake = Faker()

with app.app_context():
    db.create_all()
    print("Seeding typshii...")

    Recipe.query.delete()
    User.query.delete()
    print("Cleared old data.")

    print("Creating 15 users...")
    users = []
    for _ in range(15):
        user = User(
            username=fake.unique.user_name(),
            email=fake.unique.email()
        )
        user.password_hash = "password123"
        db.session.add(user)
        users.append(user)

    db.session.commit()

    print("Creating 15 recipes...")
    categories = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Snack']
    for _ in range(15):
        recipe = Recipe(
            title=fake.sentence(nb_words=3),
            description=fake.text(max_nb_chars=150),
            ingredients=fake.paragraph(nb_sentences=2),
            instructions=fake.paragraph(nb_sentences=3),
            category=choice(categories),
            user_id=choice(users).id
        )
        db.session.add(recipe)

    db.session.commit()
    print("✅ Done seeding 15 users and 15 recipes!")
