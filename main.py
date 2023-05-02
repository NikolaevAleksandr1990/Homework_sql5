import psycopg2


def create_db(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(20),
                last_name VARCHAR(20),
                email VARCHAR(40) NOT NULL);
            """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonenumbers(
        phones VARCHAR(11) PRIMARY KEY,
        client_id INTEGER REFERENCES clients(id)
        );
            """)
    return


def delete_db(cur):
    cur.execute("""
        DROP TABLE clients, phonenumbers CASCADE;
        """)


def add_client(cur, first_name, last_name, email, phones=None):
    cur.execute("""
            INSERT INTO clients(first_name, last_name, email)
            VALUES (%s, %s, %s)
            """, (first_name, last_name, email))
    cur.execute("""
            SELECT id from clients
            ORDER BY id DESC
            LIMIT 1
            """)
    client_id = cur.fetchone()[0]
    if phones is None:
        return client_id
    else:
        add_phone(cur, client_id, phones)
        return client_id


def add_phone(cur, client_id, phones):
    cur.execute("""
            INSERT INTO phonenumbers(phones, client_id)
            VALUES (%s, %s)
            """, (phones, client_id))
    return client_id


def change_client(cur, client_id, first_name=None, last_name=None, email=None, phones=None):
    if first_name is not None:
        cur.execute("""
                UPDATE clients SET first_name=%s WHERE id=%s
                """, (first_name, client_id))
    if last_name is not None:
        cur.execute("""
                UPDATE clients SET last_name=%s WHERE id=%s
                """, (last_name, client_id))
    if email is not None:
        cur.execute("""
                UPDATE clients SET email=%s WHERE id=%s
                """, (email, client_id))
    if phones is not None:
        add_phone(cur, client_id, phones)

    cur.execute("""
                SELECT * FROM clients;
                """)
    cur.fetchall()


def delete_phone(cur, phone):
    cur.execute("""
            DELETE FROM phonenumbers 
            WHERE phones = %s
            """, (phone,))
    return phone


def delete_client(cur, client_id):
    cur.execute("""
            DELETE FROM phonenumbers
            WHERE client_id = %s
            """, (client_id,))
    cur.execute("""
            DELETE FROM clients 
            WHERE id = %s
           """, (client_id,))
    return client_id


def find_client(cur, first_name=None, last_name=None, email=None, phone=None):
    if first_name is None:
        first_name = '%'
    else:
        first_name = '%' + first_name + '%'
    if last_name is None:
        last_name = '%'
    else:
        last_name = '%' + last_name + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if phone is None:
        cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, p.phones FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                WHERE c.first_name LIKE %s AND c.last_name LIKE %s
                AND c.email LIKE %s
                """, (first_name, last_name, email))
    else:
        cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email,p.phones FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                WHERE c.first_name LIKE %s AND c.last_name LIKE %s
                AND c.email LIKE %s AND p.phones like %s
                """, (first_name, last_name, email, phone))
    return cur.fetchall()


def all_clients(cur):
    cur.execute("""
        SELECT * FROM clients;
        """)
    print(cur.fetchall())
    cur.execute("""
        SELECT * FROM phonenumbers;
        """)
    print(cur.fetchall())


with psycopg2.connect(database='homework_5', user='postgres', password='Lolit6830023') as conn:
    with conn.cursor() as curs:
        delete_db(curs)
        create_db(curs)
        # print('БД создана')
        # Добавляем клиентов
        add_client(curs, 'Александр', 'Петров', 'petrov_a@gmail.com')
        add_client(curs, 'Константин', 'Васильев',
                   'vasilev_k@mail.ru', 79498477192)
        add_client(curs, 'Иван', 'Сорин',
                   'sorin_i@mail.com', 79218839023)
        add_client(curs, 'Вениамин', 'Попов',
                   'popov_V@mail.ru', 79040000001)
        add_client(curs, 'Анна', 'Резник',
                   'Anna_R91@yandex.ru')
        # Довавляем номер телефона
        add_phone(curs, 2, 79877876543)
        add_phone(curs, 1, 79602450948)
        # Изменяем данные клиента
        change_client(curs, 4, "Иван", None, 'sandy@outlook.com')
        # Удаляем телефонный номер клиента
        delete_phone(curs, '79602450948')
        # Удаляем клиента
        delete_client(curs, 2)
        # Найти клиента по параметрам
        find_client(curs, 'Анна')
        find_client(curs, None, None, 'sorin_i@mail.com')
        find_client(curs, 'Анна', 'Резник', 'Anna_R91@yandex.ru')
        find_client(curs, None, None, None, '79498477192')

        all_clients(curs)
