from datetime import datetime

from app.extensions import db


def now_utc():
    return datetime.utcnow()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    pin = db.Column(db.String(20), nullable=False)

    focus_led_color = db.Column(db.String(20), nullable=False, default="#d66b5d")
    break_led_color = db.Column(db.String(20), nullable=False, default="#65b891")

    face_image_path = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=now_utc)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=now_utc,
        onupdate=now_utc,
    )

    settings = db.relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    access_logs = db.relationship(
        "AccessLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    pomodoro_sessions = db.relationship(
        "PomodoroSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    tasks = db.relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "focusLedColor": self.focus_led_color,
            "breakLedColor": self.break_led_color,
            "faceImagePath": self.face_image_path,
        }


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        unique=True,
        index=True,
    )

    temperature_threshold = db.Column(db.Float, nullable=False, default=26.0)
    default_focus_minutes = db.Column(db.Integer, nullable=False, default=25)
    default_break_minutes = db.Column(db.Integer, nullable=False, default=5)

    default_led_color = db.Column(db.String(20), nullable=False, default="#d66b5d")
    focus_led_color = db.Column(db.String(20), nullable=False, default="#d66b5d")
    break_led_color = db.Column(db.String(20), nullable=False, default="#65b891")

    music_enabled = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=now_utc)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=now_utc,
        onupdate=now_utc,
    )

    user = db.relationship("User", back_populates="settings")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "temperatureThreshold": self.temperature_threshold,
            "defaultFocusMinutes": self.default_focus_minutes,
            "defaultBreakMinutes": self.default_break_minutes,
            "defaultLedColor": self.default_led_color,
            "focusLedColor": self.focus_led_color,
            "breakLedColor": self.break_led_color,
            "musicEnabled": self.music_enabled,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)

    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    presence = db.Column(db.Boolean, nullable=True)

    metadata_json = db.Column(db.JSON, nullable=False, default=dict)

    timestamp = db.Column(db.DateTime, nullable=False, default=now_utc, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "presence": self.presence,
            "metadata": self.metadata_json or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class TimelineEvent(db.Model):
    __tablename__ = "timeline_events"

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(80), nullable=False, index=True)
    message = db.Column(db.String(500), nullable=False)

    metadata_json = db.Column(db.JSON, nullable=False, default=dict)

    timestamp = db.Column(db.DateTime, nullable=False, default=now_utc, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "message": self.message,
            "metadata": self.metadata_json or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class AccessLog(db.Model):
    __tablename__ = "access_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    user_snapshot = db.Column(db.JSON, nullable=True)

    method = db.Column(db.String(80), nullable=False, default="unknown")
    success = db.Column(db.Boolean, nullable=False, default=False)
    message = db.Column(db.String(500), nullable=False, default="")

    metadata_json = db.Column(db.JSON, nullable=False, default=dict)

    timestamp = db.Column(db.DateTime, nullable=False, default=now_utc, index=True)

    user = db.relationship("User", back_populates="access_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user_snapshot,
            "method": self.method,
            "success": self.success,
            "message": self.message,
            "metadata": self.metadata_json or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class PomodoroSession(db.Model):
    __tablename__ = "pomodoro_sessions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    user_snapshot = db.Column(db.JSON, nullable=True)

    task = db.Column(db.String(300), nullable=True)
    notes = db.Column(db.Text, nullable=False, default="")

    productive = db.Column(db.Boolean, nullable=False, default=False)
    rating = db.Column(db.Integer, nullable=True)

    focus_minutes = db.Column(db.Integer, nullable=False, default=25)
    break_minutes = db.Column(db.Integer, nullable=False, default=5)
    desk_absence_count = db.Column(db.Integer, nullable=False, default=0)

    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)

    metadata_json = db.Column(db.JSON, nullable=False, default=dict)

    created_at = db.Column(db.DateTime, nullable=False, default=now_utc, index=True)

    user = db.relationship("User", back_populates="pomodoro_sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user_snapshot,
            "task": self.task,
            "notes": self.notes,
            "productive": self.productive,
            "rating": self.rating,
            "focusMinutes": self.focus_minutes,
            "breakMinutes": self.break_minutes,
            "deskAbsenceCount": self.desk_absence_count,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "endedAt": self.ended_at.isoformat() if self.ended_at else None,
            "metadata": self.metadata_json or {},
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    title = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    selected = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=now_utc, index=True)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=now_utc,
        onupdate=now_utc,
    )

    user = db.relationship("User", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "selected": self.selected,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class DeviceCommand(db.Model):
    __tablename__ = "device_commands"

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(120), nullable=False, index=True)
    value = db.Column(db.JSON, nullable=True)
    payload = db.Column(db.JSON, nullable=False, default=dict)

    status = db.Column(db.String(40), nullable=False, default="pending", index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=now_utc, index=True)
    consumed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value,
            "payload": self.payload or {},
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "consumedAt": self.consumed_at.isoformat() if self.consumed_at else None,
        }