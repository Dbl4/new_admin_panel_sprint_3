from psycopg2.extensions import connection as _connection


class PostgresLoader:
    def __init__(self, pg_conn: _connection) -> None:
        self.connection = pg_conn

    def load_data(self, films_works_id: tuple) -> dict:
        """Загрузка всех данных из Postgres для последующей вставки в ElasticSearch"""
        curs = self.get_cursor()
        curs.execute(
            f"""SELECT
               COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'person_id', p.id,
                           'person_name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null and pfw.role = 'actor'),
                   '[]'
               ) as actors,
               array_remove(array_agg(DISTINCT p.full_name)
                    FILTER (WHERE pfw.role = 'actor'), null) as actors_names,
               fw.description,
               array_remove(array_agg(DISTINCT p.full_name)
                    FILTER (WHERE pfw.role = 'director'), null) as director,
               array_agg(DISTINCT g.name) as genre,
               fw.id,
               fw.rating as imdb_rating,
               fw.title,
               COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'person_id', p.id,
                           'person_name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null and pfw.role = 'writer'),
                   '[]'
               ) as writers,
               array_remove(array_agg(DISTINCT p.full_name)
                    FILTER (WHERE pfw.role = 'writer'), null) as writers_names
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN {films_works_id}
            GROUP BY fw.id
            ORDER BY fw.modified""")

        record = curs.fetchall()
        return record

    def get_films_id(self, state: dict) -> (list, dict):
        """Получить id фильмов и новое состояние (последняя дата изменения фильма modified)"""
        curs = self.get_cursor()
        curs.execute(
            f"""SELECT
                    id,
                    to_char(modified, 'YYYY-MM-DD HH24:MI:SS.US')
                    as modified
                FROM content.film_work
                WHERE modified > '{state}'
                ORDER BY modified
                LIMIT 100;""")

        data = curs.fetchall()
        films_id = []
        for elem in data:
            films_id.append(elem.get('id'))

        new_state = data[-1].get('modified') if data else state

        return films_id, new_state

    def get_cursor(self):
        return self.connection.cursor()
