import os
if os.path.exists('db.sqlite3'):
    os.remove('db.sqlite3')
    print('Database deleted')
else:
    print('Database does not exist')
