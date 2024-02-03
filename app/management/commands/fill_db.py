import random

from django.core import management
from django.core.management.base import BaseCommand
from app.models import *
from .utils import random_date, random_timedelta


def add_buildings():
    Building.objects.create(
        name="Главное здание",
        location="2-я Бауманская ул., 5, стр. 4",
        open_hours="9:00",
        close_hours="18:00",
        image="buildings/1.png"
    )

    Building.objects.create(
        name="Учебно-лабораторный корпус",
        location="Рубцовская наб., 2/18",
        open_hours="9:00",
        close_hours="17:30",
        image="buildings/2.png"
    )

    Building.objects.create(
        name="Энергомашиностроительный корпус",
        location="Лефортовская наб., 1",
        open_hours="9:00",
        close_hours="17:30",
        image="buildings/3.png"
    )

    Building.objects.create(
        name="Специальное машиностроение",
        location="Госпитальный пер., 10",
        open_hours="9:00",
        close_hours="18:00",
        image="buildings/4.png"
    )

    Building.objects.create(
        name="Технологический корпус",
        location="2-я Бауманская ул., 7",
        open_hours="9:00",
        close_hours="17:30",
        image="buildings/5.png",
    )

    print("Услуги добавлены")


def add_permits():
    owners = CustomUser.objects.filter(is_superuser=False)
    moderators = CustomUser.objects.filter(is_superuser=True)

    if len(owners) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    buildings = Building.objects.all()

    for _ in range(30):
        permit = Permit.objects.create()
        permit.status = random.randint(2, 5)
        permit.owner = random.choice(owners)
        permit.person_count = random.randint(1, 5)
        permit.passege_date = random_date()

        if permit.status in [3, 4]:
            permit.date_complete = random_date()
            permit.date_formation = permit.date_complete - random_timedelta()
            permit.date_created = permit.date_formation - random_timedelta()
            permit.moderator = random.choice(moderators)
        else:
            permit.date_formation = random_date()
            permit.date_created = permit.date_formation - random_timedelta()

        for i in range(random.randint(1, 3)):
            permit.buildings.add(random.choice(buildings))

        permit.save()

    print("Заявки добавлены")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        management.call_command("clean_db")
        management.call_command("add_users")

        add_buildings()
        add_permits()









