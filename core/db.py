from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password

try:
    from bson import ObjectId
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
except Exception:  # pragma: no cover - used when pymongo is not installed yet
    MongoClient = None
    ObjectId = None
    PyMongoError = Exception
    ServerSelectionTimeoutError = Exception


NOW = lambda: datetime.now(timezone.utc)


SEEDS = {
    "events": [
        {"title": "Sunday Worship Service", "date": "2026-06-14", "time": "8:00 AM", "location": "ASF Glory Tabernacle", "description": "Weekly worship, prayer, teaching, and fellowship.", "capacity": "200"},
        {"title": "Youth Bible Study", "date": "2026-06-16", "time": "6:00 PM", "location": "Main Fellowship Hall", "description": "Interactive Bible study for students and young adults.", "capacity": "80"},
        {"title": "Community Outreach", "date": "2026-06-20", "time": "9:00 AM", "location": "Okitipupa Community Center", "description": "Serving families through food distribution, prayer, and care.", "capacity": "60"},
    ],
    "blogs": [
        {"title": "Finding Peace in Troubled Times", "author": "Sarah Johnson", "image": "understanding.jpg", "content": "Prayer and Scripture restore our sight when life feels uncertain. God is near, attentive, and able to guide every season.", "status": "published"},
        {"title": "My Journey to Faith", "author": "Michael Chen", "image": "page1.jpg", "content": "A testimony of how fellowship, worship, and simple care drew me closer to Christ and gave my life direction.", "status": "pending"},
    ],
    "mentors": [
        {"name": "Rev. David Thompson", "specialty": "Spiritual Formation", "experience": "15 years", "email": "david.thompson@fellowship.org", "availability": "Weekday evenings", "bio": "Helps young believers grow through prayer, Scripture, and spiritual disciplines."},
        {"name": "Dr. Grace Martinez", "specialty": "Career Guidance", "experience": "12 years", "email": "grace.martinez@fellowship.org", "availability": "Weekends", "bio": "Supports students integrating faith, calling, and professional life."},
    ],
    "resources": [
        {"title": "Bible Study Methods for Beginners", "type": "Study Guide", "link": "https://example.com/bible-study", "description": "A practical guide for personal Bible study and meditation."},
        {"title": "Faith & Work Podcast", "type": "Podcast", "link": "https://example.com/podcast", "description": "Weekly conversations about Christian faith and professional calling."},
    ],
    "alumni": [
        {"name": "Jennifer Lee", "profession": "Software Engineer", "degree": "B.S. Computer Science", "service": "Technology Ministry Lead", "bio": "Uses technology to serve people and strengthen community."},
        {"name": "Marcus Thompson", "profession": "Community Director", "degree": "B.A. Theology", "service": "Youth Mentor", "bio": "Builds programs that connect faith, service, and local impact."},
    ],
    "prayers": [
        {"author": "Sarah M.", "category": "Health", "request": "Please pray for my family as we navigate a difficult health diagnosis.", "prayer_count": 24, "anonymous": False},
        {"author": "Anonymous", "category": "Guidance", "request": "Seeking prayers for guidance in a major career decision.", "prayer_count": 18, "anonymous": True},
    ],
    "notifications": [
        {"title": "Daily Motivation", "message": "Arise, shine, for your light has come.", "audience": "all"},
    ],
}


class MemoryCollection:
    def __init__(self, name: str):
        self.name = name
        self.rows: list[dict[str, Any]] = []

    def count_documents(self, query=None):
        return len(self.find(query or {}))

    def find(self, query=None):
        query = query or {}
        rows = [row for row in self.rows if _matches(row, query)]
        return MemoryCursor(deepcopy(rows))

    def find_one(self, query):
        rows = self.find(query)
        return rows[0] if rows else None

    def insert_one(self, data):
        data = deepcopy(data)
        data.setdefault("_id", uuid4().hex)
        self.rows.append(data)
        return type("InsertOneResult", (), {"inserted_id": data["_id"]})

    def update_one(self, query, update):
        row = self.find_one(query)
        if row:
            original = next(item for item in self.rows if str(item["_id"]) == str(row["_id"]))
            original.update(update.get("$set", {}))
        return None

    def delete_one(self, query):
        self.rows = [row for row in self.rows if not _matches(row, query)]
        return None


class MemoryCursor(list):
    def sort(self, key, direction=-1):
        reverse = direction == -1
        return MemoryCursor(sorted(self, key=lambda row: str(row.get(key, "")), reverse=reverse))

    def limit(self, count):
        return MemoryCursor(self[:count])


def _matches(row, query):
    return all(str(row.get(key)) == str(value) for key, value in query.items())


class MongoRepository:
    collections = ["users", "admins", "events", "blogs", "mentors", "resources", "alumni", "prayers", "notifications", "profiles"]

    def __init__(self):
        self._client = None
        self._db = None
        self._memory = {name: MemoryCollection(name) for name in self.collections}
        self._error = ""

    def connect(self):
        if self._db is not None:
            return self._db
        if MongoClient is None:
            self._error = "pymongo is not installed; using temporary in-memory data."
            return None
        try:
            self._client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=800)
            self._client.admin.command("ping")
            self._db = self._client[settings.MONGO_DB_NAME]
            self._error = ""
        except (ServerSelectionTimeoutError, PyMongoError) as exc:
            self._error = f"MongoDB unavailable at {settings.MONGO_URI}; using temporary in-memory data. {exc}"
            self._db = None
        return self._db

    def col(self, name):
        db = self.connect()
        return db[name] if db is not None else self._memory[name]

    def status(self):
        self.connect()
        return {"database": settings.MONGO_DB_NAME, "connected": self._db is not None, "message": self._error}

    def ensure_seeded(self):
        for name, rows in SEEDS.items():
            col = self.col(name)
            if col.count_documents({}) == 0:
                for row in rows:
                    self.create(name, row)
        if self.col("admins").count_documents({}) == 0:
            self.create("admins", {"name": "ASF Super Admin", "email": "admin@asfoaustech.local", "password": make_password("admin12345"), "role": "superadmin"})

    def normalize(self, row):
        if not row:
            return None
        row = dict(row)
        row["id"] = str(row.pop("_id"))
        return row

    def object_id(self, value):
        if ObjectId is not None:
            try:
                return ObjectId(value)
            except Exception:
                return value
        return value

    def list(self, name, limit=100):
        return [self.normalize(row) for row in self.col(name).find({}).sort("created_at", -1).limit(limit)]

    def get(self, name, item_id):
        return self.normalize(self.col(name).find_one({"_id": self.object_id(item_id)}))

    def create(self, name, data):
        data = self.clean(data)
        data.setdefault("created_at", NOW())
        return str(self.col(name).insert_one(data).inserted_id)

    def update(self, name, item_id, data):
        data = self.clean(data)
        data["updated_at"] = NOW()
        self.col(name).update_one({"_id": self.object_id(item_id)}, {"$set": data})

    def delete(self, name, item_id):
        self.col(name).delete_one({"_id": self.object_id(item_id)})

    def clean(self, data):
        cleaned = {}
        for key, value in data.items():
            if key.startswith("csrf") or key in {"next"}:
                continue
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned

    def find_user(self, email):
        return self.normalize(self.col("users").find_one({"email": email.lower().strip()}))

    def current_user(self, request):
        user_id = request.session.get("user_id")
        return self.get("users", user_id) if user_id else None

    def current_admin(self, request):
        admin_id = request.session.get("admin_id")
        return self.get("admins", admin_id) if admin_id else None

    def authenticate(self, collection, email, password):
        row = self.normalize(self.col(collection).find_one({"email": email.lower().strip()}))
        if row and check_password(password, row.get("password", "")):
            return row
        return None


repository = MongoRepository()
