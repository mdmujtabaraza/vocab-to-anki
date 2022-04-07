import sqlite3

from src.lib.helpers import get_root_path

connection = sqlite3.connect(f'{get_root_path()}data.db')
cursor = connection.cursor()

# https://stackoverflow.com/a/44951682
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags(
tag TEXT NOT NULL COLLATE NOCASE,
PRIMARY KEY(tag)
)
""")
# dt datetime default current_timestamp

# Without a COLLATE INDEX our queries will do a full table scan
# EXPLAIN QUERY PLAN SELECT * FROM tags WHERE tag = 'some-tag;
# output: SCAN TABLE tags

# When COLLATE NOCASE index is present, the query does not scan all rows.
# EXPLAIN QUERY PLAN SELECT * FROM tags WHERE tag = 'some-tag';
# output: SEARCH TABLE tags USING INDEX idx_nocase_tags (tag=?)

# Refer: https://www.designcise.com/web/tutorial/how-to-do-case-insensitive-comparisons-in-sqlite
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_nocase_tags ON tags (tag COLLATE NOCASE)
""")
