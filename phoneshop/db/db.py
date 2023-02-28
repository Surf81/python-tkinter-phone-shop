import sqlite3


class DB:
    def __init__(self, dbname):
        self.connect = sqlite3.connect(dbname)
        self.check_or_create_auth_tables()
        self.check_or_create_phone_tables()


        self.add_phone({
            "nomination": "iPhone",
            "price": 25000,
            "components": {
                "ram": "4 Gb",
                "cpu": "A13",
                "storage": "128 Gb",
                "color": "black",
            }
        })


    def add_phone(self, content: dict) -> int:
        """
        Inners:
                 content: dict
                    need contains:
                    "nomination": str - name of phone
                    "price": int | float - price of phone
                    "components": dict - parametrs of phone
        Returns: int 
                 value of phone_id in database table "phone"
                 or -1 if dublicate
        """
        cur = self.connect.cursor()

        # Добавить отсутствующие конпоненты характеристик телефонов
        components = tuple((characteristic.strip().lower(), value.strip()) for characteristic, value in content['components'].items())
        cur.executemany("""INSERT INTO component(characteristic, value) 
            SELECT c1.characteristic, c1.value
            FROM
                (SELECT characteristic, val.column2 as value
                FROM 
                (
                    VALUES (?, ?)
                ) val
                JOIN characteristic ON characteristic=val.column1) c1
            LEFT JOIN
                component c2 ON c1.characteristic = c2.characteristic
                                AND LOWER(c1.value)=LOWER(c2.value)
            WHERE c2.component_id IS NULL;
            """, components)
        self.connect.commit()        

        # Старт транзакции
        cur.execute("""BEGIN;""")

        # Добавить новую запись телефона        
        cur.execute("""INSERT INTO phone(nomination, price)
            VALUES (?, ?)
            RETURNING phone_id;
            """, (content["nomination"], content["price"]))
        phone_id = cur.fetchone()[0]
        print("phone_id: ", phone_id)

        # Настройка компонентов телефона
        phone_components = tuple((phone_id, characteristic, value) for characteristic, value in components)
        cur.executemany("""INSERT INTO phone_component(phone_id, component_id, characteristic) 
            SELECT DISTINCT c1.phone_id, component_id, c2.characteristic
            FROM
                (SELECT val.column1 as phone_id, characteristic, val.column3 as value
                FROM 
                (
                    VALUES (?, ?, ?)
                ) val
                JOIN characteristic ON characteristic=val.column2) c1
            JOIN
                component c2 ON c1.characteristic = c2.characteristic
                                AND LOWER(c1.value)=LOWER(c2.value);
            """, phone_components)

        # Проверка на дублирование телефона с совпадающими характеристиками
        cur.execute("""WITH cte AS
            (
                SELECT nomination, price, component_id
                FROM phone
                JOIN phone_component USING(phone_id)
                WHERE phone_id = ?
            )
            SELECT phone_id
            FROM phone
            JOIN phone_component USING(phone_id)
            WHERE phone_id != ?
                  AND (nomination, price, component_id) IN (SELECT * FROM cte)
            GROUP BY phone_id
            HAVING COUNT(*) = (SELECT COUNT(*) FROM cte);
        """, (phone_id, phone_id))
        
        dublicate_phone_id = cur.fetchone()

        if dublicate_phone_id:
            cur.execute("""ROLLBACK;""")
        else:
            cur.execute("""COMMIT;""")

        self.connect.commit()

        if dublicate_phone_id:
            return -1
        
        return phone_id



    def check_or_create_auth_tables(self):
        cur = self.connect.cursor()

        # Если таблица ролей отсутствует, то она будет создана
        cur.execute("""CREATE TABLE IF NOT EXISTS role(
            role CHAR(5) PRIMARY KEY NOT NULL,
            descr CHAR(16) NOT NULL);
            """)
        self.connect.commit()

        # Если роли пользователя и/или администратора отсутствуют, они будут добавлены
        roles = [
            ("user", "Пользователь"),
            ("admin", "Администратор"),
        ]
        cur.executemany("""INSERT INTO role(role, descr) 
            SELECT val.column1 as role, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN role ON role=val.column1
            WHERE role IS NULL;    
            """, roles)
        self.connect.commit()        


        # Если таблица пользователей отсутствует, то она будет создана
        cur.execute("""CREATE TABLE IF NOT EXISTS user(
            login CHAR(16) PRIMARY KEY NOT NULL,
            password CHAR(16) NOT NULL,
            firstname CHAR(50),
            secondname CHAR(50),
            patronymic CHAR(50),
            exist BOOLEAN NOT NULL);
            """)
        self.connect.commit()

        # Добавление дефолтной записи администратора, если отсутствует
        users = [
            ("admin", "0000", 1),
        ]
        cur.executemany("""INSERT INTO user(login, password, exist) 
            SELECT val.column1 as login, val.column2 as password, val.column3 as exist
            FROM 
            (
                VALUES (?, ?, ?)
            ) val
            LEFT JOIN user ON login=val.column1
            WHERE login IS NULL;    
            """, users)
        self.connect.commit()        


        # Если таблица сопоставления ролей отсутствует, она будет создана
        cur.execute("""CREATE TABLE IF NOT EXISTS user_roles(
            user_roles_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            login CHAR(16) NOT NULL,
            role CHAR(5) NOT NULL,
            prefer BOOLEAN NOT NULL,
            FOREIGN KEY (login) REFERENCES user(login) ON DELETE CASCADE,
            FOREIGN KEY (role) REFERENCES role(role) ON DELETE CASCADE,
            UNIQUE(login, role));
            """)
        self.connect.commit()

        # Добавление прав для записи администратора, если отсутствуют
        alailable_roles = [
            ("admin", "admin", 1),
            ("admin", "user", 0),
        ]
        cur.executemany("""INSERT INTO user_roles(login, role, prefer) 
            SELECT login, role, s.prefer
            FROM
                (SELECT login, role, val.column3 as prefer
                FROM 
                (
                    VALUES (?, ?, ?)
                ) val
                JOIN user ON login=val.column1
                JOIN role ON role=val.column2) s
            LEFT JOIN
                user_roles USING(login, role)
            WHERE user_roles_id IS NULL;    
            """, alailable_roles)
        self.connect.commit()        

        # Всем пользователям без каких-либо ролей проставляем роль user
        user_roles = [
            ("user", 1),
        ]
        cur.executemany("""INSERT INTO user_roles(login, role, prefer) 
            SELECT login, s.role, s.prefer
            FROM
                (SELECT login, role, val.column2 as prefer
                FROM 
                (
                    VALUES (?, ?)
                ) val
                JOIN role ON role=val.column1
                CROSS JOIN user) s
            LEFT JOIN
                user_roles USING(login)
            WHERE user_roles_id IS NULL;    
            """, user_roles)
        self.connect.commit()        


    def check_or_create_phone_tables(self):
        cur = self.connect.cursor()

        # Если таблица типов параметров отсутствует, то она будет создана
        cur.execute("""CREATE TABLE IF NOT EXISTS characteristic(
            characteristic CHAR(16) PRIMARY KEY NOT NULL,
            descr CHAR(24) NOT NULL);
            """)
        self.connect.commit()

        # Если типы параметров отсутствуют, они будут добавлены
        params = [
            ("ram", "объем ОЗУ"),
            ("storage", "объем хранилища"),
            ("cpu", "процессор"),
            ("color", "цвет"),
            ("pricedrop", "уценка"),
        ]
        cur.executemany("""INSERT INTO characteristic(characteristic, descr) 
            SELECT val.column1 as characteristic, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN characteristic ON characteristic=val.column1
            WHERE characteristic IS NULL;    
            """, params)
        self.connect.commit()        

        # Если таблица компонентов отсутствует, то она будет создана
        cur.execute("""CREATE TABLE IF NOT EXISTS component(
            component_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            characteristic CHAR(16) NOT NULL,
            value CHAR(24) NOT NULL,
            FOREIGN KEY (characteristic) REFERENCES characteristic(characteristic),
            UNIQUE(characteristic, value));
            """)
        self.connect.commit()

        # Если таблица телефонов отсутствует, то она будет создана
        cur.execute("""CREATE TABLE IF NOT EXISTS phone(
            phone_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            nomination CHAR(24) NOT NULL,
            price NUMERIC(10.2) NOT NULL,
            CHECK (price > 0));
            """)
        self.connect.commit()

        # Если таблица телефонов отсутствует, то она будет создана
        cur.execute("""CREATE TABLE IF NOT EXISTS phone_component(
            phone_component_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            phone_id INTEGER NOT NULL,
            component_id INTEGER NOT NULL,
            characteristic CHAR(16) NOT NULL,
            FOREIGN KEY (phone_id) REFERENCES phone(phone_id),
            FOREIGN KEY (component_id) REFERENCES component(component_id),
            UNIQUE(phone_id, characteristic));
            """)
        self.connect.commit()



