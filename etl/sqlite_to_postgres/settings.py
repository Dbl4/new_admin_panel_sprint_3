from models import Filmwork, Genre, Person, GenreFilmwork, \
    PersonFilmwork

schema = 'content'

tables = {
    Filmwork: 'film_work',
    Genre: 'genre',
    Person: 'person',
    GenreFilmwork: 'genre_film_work',
    PersonFilmwork: 'person_film_work'
}
