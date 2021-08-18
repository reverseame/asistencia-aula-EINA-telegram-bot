import datetime
from peewee import (Model, DateTimeField, ForeignKeyField, BigIntegerField, CharField,
                    IntegerField, TextField, OperationalError, BooleanField)
from playhouse.migrate import migrate, SqliteMigrator, SqliteDatabase

class TelegramChat(Model):
    chat_id = IntegerField(unique=True)
    known_at = DateTimeField(default=datetime.datetime.now)
    tg_type = CharField()
    last_contact = DateTimeField(default=datetime.datetime.now)
    delete_soon = BooleanField(default=False)

    @property
    def is_group(self):
        return self.chat_id < 0

    def touch_contact(self):
        self.last_contact = datetime.datetime.now()
        self.save()

class Subscription(Model):
    tg_chat = ForeignKeyField(TelegramChat, related_name="subscriptions")
    u_id = TextField()
    known_at = DateTimeField(default=datetime.datetime.now)

class Room(Model):
    tg_chat = ForeignKeyField(TelegramChat, related_name="rooms")
    room_name = TextField()
    last_time = DateTimeField(default=datetime.datetime.now)
    still_in_room = BooleanField(default=True)

# Create tables
for t in (TelegramChat, Subscription, Room):
    t.create_table(fail_silently=True)


# Migrate new fields. TODO: think of some better migration mechanism
db = SqliteDatabase('peewee.db', timeout=10)
