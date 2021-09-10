import random
from project import db
from project.models import User, Mentor, Mentee
from faker import Faker
import pandas as pd
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime
import pytz


tf = TimezoneFinder()
geolocator = Nominatim(user_agent='myapplication')
fake = Faker()


db.drop_all()
db.create_all()


# city_df = pd.read_csv("cities.csv", encoding='latin-1')
field_df = pd.read_csv("fields_of_study.csv")


languages = ["English", "Hindi", "Kannada"]
locations = ["Delhi", "Mumbai", "Kolkata", "Bangalore", "Chennai", "Hyderabad"]
# cities = city_df["name"].tolist()
cities = ["Delhi", "Mumbai", "Bangalore" "London", "New York",
          "France", "Moscow", "Tokyo", "Dubai", "Singapore", "Barcelona", "Los Angeles",
          "Madrid", "Rome", "Chicago", "Toronto", "San Francisco", "Abu Dhabi", "Amsterdam", ]
fields = field_df["Major_Category"].unique()


num = 100
roles = []
for _ in range(num):
    profile = fake.profile()
    urole = random.choices(["MENTOR", "MENTEE"], weights=(0.3, 0.7), k=1)[0]
    roles.append(urole)
    user = User(
        fullname=profile["name"],
        username=profile["username"],
        email=profile["mail"],
        phone=fake.msisdn(),
        password=fake.password(), # bcrypt.generate_password_hash(fake.password()).decode('utf-8')
        urole=urole
    )
    db.session.add(user)
db.session.commit()
print("users added")


i = 0
while i < 100:
    if i%10 == 0:
        print(i)
    try:
        urole = roles[i]
        if urole == "MENTOR":
            city = random.choice(cities)
            location = geolocator.geocode(city)
            t_zone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            pacific_now = datetime.datetime.now(pytz.timezone(t_zone))
            offset = pacific_now.utcoffset().total_seconds() / 60 / 60
            mentor = Mentor(
                hobbies=fake.sentence(),
                city=city,
                lat=location.latitude,
                long=location.longitude,
                time_delta=offset,
                gender=random.choice(["Male", "Female"]),
                language=random.choice(languages),
                expertise_1=random.choice(fields),
                bq_1=fake.sentence(),
                bq_2=fake.sentence(),
                ready=True
            )
            mentor.user_id = i+1
            db.session.add(mentor)

        elif urole == "MENTEE":
            city = random.choice(cities)
            location = geolocator.geocode(city)
            t_zone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            pacific_now = datetime.datetime.now(pytz.timezone(t_zone))
            offset = pacific_now.utcoffset().total_seconds() / 60 / 60
            mentee = Mentee(
                hobbies=fake.sentence(),
                city=city,
                lat=location.latitude,
                long=location.longitude,
                time_delta=offset,
                gender=random.choice(["Male", "Female"]),
                gender_pref=random.choice(["Male", "Female"]),
                language_pref=random.choice(languages),
                aspiration=random.choice(fields),
                bq_1=fake.sentence(),
                bq_2=fake.sentence(),
                ready=True
            )
            mentee.user_id = i+1
            db.session.add(mentee)
    except Exception as e:
        continue
    i += 1
db.session.commit()
