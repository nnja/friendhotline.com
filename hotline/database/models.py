# Copyright 2019 Alethea Katherine Flowers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Low-level database primitives. Moved here to prevent bleeding db-specific
stuff into the higher-level interface."""

import datetime
import enum

import peewee

db = peewee.Proxy()


class BaseModel(peewee.Model):
    class Meta:
        database = db


class SerializableField(peewee.TextField):
    def __init__(self, cls, *args, **kwargs):
        self._cls = cls
        super().__init__(*args, **kwargs)

    def db_value(self, value):
        return value.serialize()

    def python_value(self, value):
        return self._cls.deserialize(value)


class Number(BaseModel):
    number = peewee.TextField()
    country = peewee.CharField(default="US")
    features = peewee.TextField(index=False)


Number.add_index(Number.number)


class Hotline(BaseModel):
    # Always required stuff.
    name = peewee.TextField()
    slug = peewee.CharField(unique=True)

    # Number assignment.
    # Stored as destructured as well to speed things up a little.
    primary_number = peewee.TextField(null=True)
    primary_number_id = peewee.ForeignKeyField(Number, null=True)
    country = peewee.CharField(default="US")

    # TODO NZ: pull these out of the code
    # Information fields.
    # coc_link = peewee.TextField(null=True, index=False)
    # website = peewee.TextField(null=True, index=False)
    # contact_email = peewee.TextField(null=True, index=False)
    # location = peewee.TextField(null=True, index=False)

    # Customizations.
    # TODO NZ: Change the default greeting message
    # hint: "Thank you for calling the Code of Conduct hotline"
    voice_greeting = peewee.TextField(null=True, index=False)


Hotline.add_index(Hotline.slug)
Hotline.add_index(Hotline.primary_number)


# TODO NZ: Refactor, change this name
class HotlineMember(BaseModel):
    """Members are part of the hotline, but not necessarily able to edit
    hotline details."""

    hotline = peewee.ForeignKeyField(Hotline, backref="members")
    name = peewee.TextField()
    number = peewee.TextField()
    verified = peewee.BooleanField()


HotlineMember.add_index(HotlineMember.hotline, HotlineMember.verified)
HotlineMember.add_index(HotlineMember.number, HotlineMember.verified)


class HotlineAdmin(BaseModel):
    """Organizers are able to edit hotline details, but aren't necessarily part
    of the hotline."""

    hotline = peewee.ForeignKeyField(Hotline, backref="admins")
    user_id = peewee.CharField(null=True)
    user_name = peewee.TextField(null=True)
    user_email = peewee.TextField()


HotlineAdmin.add_index(HotlineAdmin.user_id)


# TODO NZ: Keep the audit log, but remove from the view
class AuditLog(BaseModel):
    timestamp = peewee.DateTimeField(default=datetime.datetime.utcnow)
    kind = peewee.IntegerField()
    description = peewee.TextField(null=True)
    hotline = peewee.ForeignKeyField(Hotline, backref="auditlogs", null=True)
    user = peewee.CharField(null=True)
    metadata = peewee.TextField(null=True)
    reporter_number = peewee.TextField(null=True, index=False)


AuditLog.add_index(AuditLog.hotline, AuditLog.timestamp)


class BlockList(BaseModel):
    timestamp = peewee.DateTimeField(default=datetime.datetime.utcnow)
    hotline = peewee.ForeignKeyField(Hotline, backref="blocklist")
    number = peewee.TextField()
    blocked_by = peewee.TextField(null=True)
