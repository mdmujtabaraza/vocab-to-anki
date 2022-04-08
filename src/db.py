import sqlite3


def create_connection(db_path):
    """ create a database connection to the SQLite database
    :param db_path: Path to db
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


def create_tag(conn, tag):
    """
    Create a new tag
    :param conn:
    :param tag:
    :return:
    """

    sql = ''' INSERT OR REPLACE INTO tags (tag) VALUES (?) '''
    cur = conn.cursor()
    cur.execute(sql, tag)
    conn.commit()

    return cur.lastrowid


def select_all_tags(conn):
    """
    Query all rows in the tags table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT tag FROM tags ORDER BY tag DESC LIMIT 5")

    rows = cur.fetchall()

    # for row in rows:
    #     print(row)

    return rows


def select_tags_which_contains(conn, tag):
    """
    Query tags by tag
    :param conn: the Connection object
    :param tag:
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT tag FROM tags WHERE tag LIKE '%{tag}%' ORDER BY tag DESC LIMIT 5")

    rows = cur.fetchall()

    # for row in rows:
    #     print(row)

    return rows
