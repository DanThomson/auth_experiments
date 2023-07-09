

def get_user(user_id):
    connection = get_connection()
    return connection.execute('SELECT * FROM user WHERE id = ?', (user_id, )).fetchone()


def create_user(id_, name, email, profile_pic):
    connection = get_connection()
    connection.execute(
        'INSERT INTO user (id, name, email, profile_pic)'
        'VALUES (?, ?, ?, ?)',
        (id_, name, email, profile_pic),
    )
    connection.commit()
