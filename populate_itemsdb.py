from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import User, Movie, Category, pragma_fk_conn

engine = create_engine('sqlite:///items.db')
event.listen(engine, "connect", pragma_fk_conn)
session = sessionmaker(bind=engine)()

print "Clearing database..."

session.query(User).delete()
session.query(Category).delete()
session.commit()

for u in session.query(User).all():
    print u.name

for c in session.query(Category).all():
    print c.name

for m in session.query(Movie).all():
    print m.user_id + " " + str(m.category_id)

categories = ["Western", "Drama", "Comedy", "Scifi", "Bad Movie"]

print "Adding categories..."

for c in categories:
    category = Category(name=c)
    session.add(category)

session.commit()

print "Adding user..."

user = User(name="Seth Brenneman", email="sethbrenneman@gmail.com")
session.add(user)
session.commit()

print "Adding movies..."

movies = [{"name": "The Good, the Bad, and the Ugly", "description": "Three men struggle against each other to recover a hidden sack of gold", "category": "Western"},
          {"name": "Once Upon a Time in the West", "description": "Vengeance, greed, choo choo trains, and harmonicas", "category": "Western"},
          {"name": "Fistful of Dollars", "description": "A shrewd gunfighter plays both sides of two feuding families", "category": "Western"},
          {"name": "For a Few Dollars More", "description": "Bounty hunters and bank robbers in the barren West", "category": "Western"},
          {"name": "Mystic River", "description": "A haunting incident from the past between three friends resurfaces during a daughter's murder", "category": "Drama"},
          {"name": "Bridge Over the River Kwai", "description": "An English army regiment captured by Japanese forces is forced to build a bridge", "category": "Drama"},
          {"name": "Lawrence of Arabia", "description": "T.E. Lawrence works to unite Arab tribes during WWI", "category": "Drama"},
          {"name": "The Sting", "description": "Con-men try for one last big score", "category": "Drama"},
          {"name": "Seven Samurai", "description": "In feudal Japan, seven samurai work to defend a village from raiders", "category": "Drama"},
          {"name": "Airplane!", "description": "A washed up pilot with a drinking problem must land an airplane in an emergency", "category": "Comedy"},
          {"name": "Kind Hearts and Coronets", "description": "A distant disowned relative tries to kill eight other heirs to inherit a fortune", "category": "Comedy"},
          {"name": "Dr. Strangelove", "description": "An insane renegade general launches a nuclear strike against the USSR", "category": "Comedy"},
          {"name": "Robin Hood: Men in Tights", "description": "Robin hood and his merry men must thwart the Sherriff of Nottingham", "category": "Comedy"},
          {"name": "Star Wars: A New Hope", "description": "Luke Skywalker and friends must save Princess Leia and the rest of the galaxy", "category": "Scifi"},
          {"name": "Inception", "description": "A team who can invade people's dreams works to plant an idea in the mind of a corparate exec", "category": "Scifi"},
          {"name": "Interstellar", "description": "Humanity sends a team of scientists to look for a suitable planet to colonize", "category": "Scifi"},
          {"name": "Samurai Cop", "description": "A cop trained in the way of the samurai takes on an LA gangster", "category": "Bad Movie"},
          {"name": "The Room", "description": "Good guy Johnny just can't catch a break", "category": "Bad Movie"},
          {"name": "Plan 9 From Outer Space", "description": "Aliens try to stop earth from developing a destructive superweapon", "category": "Bad Movie"}]

for m in movies:
    category = session.query(Category).filter(
        Category.name == m["category"]).one()
    movie = Movie(name=m["name"], description=m["description"],
                  user_id=user.id, category_id=category.id)
    session.add(movie)
session.commit()

users = session.query(User).all()
