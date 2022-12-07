import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Filmwork:
    creation_date: datetime
    created: datetime
    modified: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = field(default='')
    description: str = field(default='')
    file_path: str = field(default='')
    rating: float = field(default=0.0)
    type: str = field(default='')


@dataclass
class Genre:
    name: str
    created: datetime
    modified: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    description: str = field(default='')


@dataclass
class Person:
    full_name: str
    created: datetime
    modified: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class GenreFilmwork:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmwork:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    created: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    role: str = field(default='')
