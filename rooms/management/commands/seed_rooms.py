import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms import models as room_models
from users import models as user_models
# from rooms import models as room_models
# from rooms.models import Amenity

class Command(BaseCommand):

    help = "This command creates many users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            default=2, type=int,
            help="How many users do you want to create?",
        )

    def handle(self, *args, **options):
        
        number = options.get("number", 1)
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all() # get all users from database
        room_types = room_models.RoomType.objects.all()

        seeder.add_entity(room_models.Room, number, {
            "name": lambda x: seeder.faker.address(),
            "host": lambda x: random.choice(all_users),
            "room_type": lambda x: random.choice(room_types),
            "guests": lambda x: random.randint(0, 20),
            "price": lambda x: random.randint(0, 300),
            "beds": lambda x: random.randint(0, 5),
            "bedrooms": lambda x: random.randint(0, 5),
            "baths": lambda x: random.randint(0, 5)
        })

        created_photos = seeder.execute()
        created_clean = flatten(list(created_photos.values())) # purify data

        amenities = room_models.Amenity.objects.all()
        facilities = room_models.Facility.objects.all()
        rules = room_models.HouseRule.objects.all()
        
        for pk in created_clean: # pk = primary key
            room = room_models.Room.objects.get(pk=pk)
            for i in range(3, random.randint(10, 30)):
                room_models.Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    room=room,
                    file=f"room_photos/{random.randint(1, 31)}.webp"
                )

            for a in amenities:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.amenities.add(a) # how to add something in many to many field
            for f in facilities:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.facilities.add(f)
            for r in rules:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.house_rules.add(r)

        self.stdout.write(self.style.SUCCESS(f"{number} rooms created!"))