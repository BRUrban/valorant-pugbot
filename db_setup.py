from helpers import sqlite_create_connection, sqlite_create_table

def main():
    db = 'vbot.db'

    create_queues_table = '''CREATE TABLE IF NOT EXISTS queues (
    id integer PRIMARY KEY,
    timestamp TEXT); '''

    create_queued_players_table = '''CREATE TABLE IF NOT EXISTS queued_players (
    id integer PRIMARY KEY,
    queue_id integer NOT NULL,
    username text NOT NULL,
    team_id text NOT NULL,
    is_captain bool NOT NULL CHECK (is_captain IN (0,1))
    ); '''

    conn = sqlite_create_connection(db)

    if conn is not None:
        sqlite_create_table(conn, create_queues_table)
        sqlite_create_table(conn, create_queued_players_table)
        print('Tables created!')
    else:
        print("Error, cannot create the Database connection!")


if __name__ == '__main__':
    main()
