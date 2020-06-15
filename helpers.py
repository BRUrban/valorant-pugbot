import sqlite3
from sqlite3 import Error
import discord


def filter_and_format_players(team, queued_users):
    #users = list(filter(lambda player: player['team'] == team, queued_users))
    #usernames = []
    #for user in users:
    #    usernames.append(user['username'])
    formatted_usernames = """
    {}
    """.format("\n".join(queued_users[0:]))

    return([formatted_usernames, queued_users])


def sqlite_create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(str(db_file))
        print('connectred to ' + str(db_file))
    except Error as e:
        print(e)

    return conn


def sqlite_create_table(conn, schema):
    try:
        c = conn.cursor()
        c.execute(schema)
    except Error as e:
        print(e)

def sqlite_insert(conn, table, payload):
    print(payload)
    if table == 'queues':
        sql_string = f'''INSERT into {table}(timestamp) VALUES ({payload});'''
        print(sql_string)
        sql = (sql_string)
    elif table == 'queued_players':
        sql_string= f'''INSERT into {table}(queue_id, username, team_id, is_captain) VALUES ({payload});'''
        print(sql_string)
        sql = (sql_string)
    else:
        print('Error, invalid table specified.')
    print(sql)
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    return c.lastrowid

def sqlite_select(conn, table, selection, conditional=''):
    c = conn.cursor()
    print(f'SELECT {selection} FROM {table}{conditional}')
    sql_string = f'SELECT {selection} FROM {table}{conditional};'
    c.execute(sql_string)
    results = [row[0] for row in c.fetchall()]
    print(results)

    return results

def sqlite_update(conn, table, updates, conditional=''):
    c = conn.cursor()
    sql_string = f'UPDATE {table} SET {str(updates)}{conditional};'
    print(sql_string)
    c.execute(sql_string)
    conn.commit()
    results = c.fetchall()

    return results

def sqlite_delete(conn, table, conditional):
    c = conn.cursor()
    sql_string = f'DELETE FROM {table}{conditional}'
    print(sql_string)
    c.execute(sql_string)
    conn.commit()
    results = c.fetchall()

    return results

def players_embed(conn):
    current_queue_id = sqlite_select(conn, 'queues', 'id', ' ORDER BY id DESC LIMIT 1')
    players_conditional = f' WHERE queue_id={current_queue_id[0]}'
    unpicked_conditional = f' WHERE (queue_id={current_queue_id[0]} AND team_id=0)'
    t1_conditional = f' WHERE (queue_id={current_queue_id[0]} AND team_id=1)'
    t2_conditional = f' WHERE (queue_id={current_queue_id[0]} AND team_id=2)'

    player_list = sqlite_select(conn, 'queued_players', 'username', players_conditional)
    print(player_list)
    sql_unpicked_users = sqlite_select(conn, 'queued_players', 'username', unpicked_conditional)
    sql_t1_users = sqlite_select(conn, 'queued_players', 'username', t1_conditional)
    sql_t2_users = sqlite_select(conn, 'queued_players', 'username', t2_conditional)

    unpicked_users = filter_and_format_players('0', sql_unpicked_users)
    t1_users = filter_and_format_players('1', sql_t1_users)
    t2_users = filter_and_format_players('2', sql_t2_users)
    embed = discord.Embed(title="Valorant Queue", description="Players in Queue:", color=3447003)

    if player_list:
        if ((unpicked_users[0]).strip()):
            embed.add_field(name="Waiting in Queue:", value=str(unpicked_users[0]), inline=False)
        if ((t1_users[0]).strip()):
            embed.add_field(name="Team 1:", value=str(t1_users[0]), inline=True)
        if ((t2_users[0]).strip()):
            embed.add_field(name="Team 2:", value=str(t2_users[0]), inline=True)
    else:
        embed.add_field(name='\u200b', value='Queue is currently empty', inline=True)

    return embed
