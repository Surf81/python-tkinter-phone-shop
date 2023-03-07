import sqlite3

from core.settings import *


class DB:
    def __init__(self, dbname):
        self.connect = sqlite3.connect(dbname)
        self.check_or_create_auth_tables()
        self.check_or_create_phone_tables()

    def close(self):
        self.connect.close()

    def is_free_login(self, login):
        cur = self.connect.cursor()
        cur.execute(
            """SELECT login
            FROM user
            WHERE login=?;
        """,
            (login,),
        )
        return not cur.fetchone()

    def get_user_list(self):
        cur = self.connect.cursor()
        cur.execute(
            """SELECT login, 
                              password, 
                              COALESCE(firstname, ''), 
                              COALESCE(secondname, ''), 
                              COALESCE(patronymic, ''), 
                              role, 
                              descr, 
                              exist
            FROM user
            JOIN user_roles USING(login)
            JOIN role USING(role)
            ORDER BY exist DESC, login, role;
        """,
        )
        records = cur.fetchall()

        users = dict()
        for (
            login,
            password,
            firstname,
            secondname,
            patronymic,
            role,
            descr,
            exist,
        ) in records:
            user = users.setdefault(login, dict())
            user["login"] = login
            user["password"] = password
            user["firstname"] = firstname
            user["secondname"] = secondname
            user["patronymic"] = patronymic
            role_dict = user.setdefault("role", dict())
            role_dict[role] = descr
            user["exist"] = exist
        return users

    def get_user(self, login):
        cur = self.connect.cursor()
        cur.execute(
            """SELECT login, password, 
                              COALESCE(firstname, ''), 
                              COALESCE(secondname, ''), 
                              COALESCE(patronymic, ''), 
                              role, 
                              descr, 
                              exist
            FROM user
            JOIN user_roles USING(login)
            JOIN role USING(role)
            WHERE login=?;
        """,
            (login,),
        )
        records = cur.fetchall()

        user = dict()
        for (
            login,
            password,
            firstname,
            secondname,
            patronymic,
            role,
            descr,
            exist,
        ) in records:
            user["login"] = login
            user["password"] = password
            user["firstname"] = firstname
            user["secondname"] = secondname
            user["patronymic"] = patronymic
            role_dict = user.setdefault("role", dict())
            role_dict[role] = descr
            user["exist"] = exist
        return user

    def check_user(self, login: str, password: str) -> dict:
        cur = self.connect.cursor()
        cur.execute(
            """SELECT COALESCE(firstname, ''), 
                              COALESCE(secondname, ''), 
                              COALESCE(patronymic, ''), 
                              role, 
                              descr
            FROM user
            JOIN user_roles USING(login)
            JOIN role USING(role)
            WHERE login=? AND password=? AND exist;
        """,
            (login, password),
        )
        records = cur.fetchall()

        roles = dict()
        for firstname, secondname, patronymic, role, descr in records:
            role_dict = roles.setdefault(role, dict())
            role_dict["login"] = login
            role_dict["firstname"] = firstname
            role_dict["secondname"] = secondname
            role_dict["patronymic"] = patronymic
            role_dict["role"] = role
            role_dict["description"] = descr

        return roles

    def new_user(self, userdata: dict) -> dict:
        cur = self.connect.cursor()
        cur.execute(
            """INSERT INTO user(login, password, firstname, secondname, patronymic, exist)
            SELECT val.column1 as login, 
                   val.column2 as password, 
                   val.column3 as firstname, 
                   val.column4 as secondname, 
                   val.column5 as patronymic,
                   val.column6 as exist
            FROM 
            (
                VALUES(?, ?, ?, ?, ?, ?)
            ) val
            LEFT JOIN 
                user ON login=val.column1
            WHERE login IS NULL
            RETURNING *;
        """,
            (
                userdata["login"],
                userdata["password"],
                userdata.get("firstname", ""),
                userdata.get("secondname", ""),
                userdata.get("patronymic", ""),
                userdata.get("exist", 1),
            ),
        )
        records = cur.fetchone()

        if not records:
            return {}

        if roles := userdata.get("roles"):
            newuser = tuple((userdata["login"], role) for role in roles)
        else:
            newuser = ((userdata["login"], "user"),)
        cur.executemany(
            """INSERT INTO user_roles(login, role)
            SELECT val.column1 as login, val.column2 as role
            FROM
            (
                VALUES(?, ?)
            ) val;
        """,
            newuser,
        )
        self.connect.commit()

        return self.check_user(userdata["login"], userdata["password"])

    def update_user(self, userdata: dict):
        cur = self.connect.cursor()
        cur.execute(
            """UPDATE user
            SET password = ?,
                firstname = ?,
                secondname = ?,
                patronymic = ?,
                exist = ?
            WHERE login=?;
        """,
            (
                userdata["password"],
                userdata.get("firstname", ""),
                userdata.get("secondname", ""),
                userdata.get("patronymic", ""),
                userdata.get("exist", 1),
                userdata["login"],
            ),
        )

        roles = tuple((userdata["login"], role) for role in userdata.get("roles"))
        cur.execute("CREATE TEMPORARY TABLE IF NOT EXISTS tbl(login, role);")
        cur.executemany(
            """INSERT INTO tbl(login, role)        
        SELECT val.column1 as login, val.column2 as role
        FROM
            (
                VALUES               
                (?, ?)
            ) val; 
        """,
            roles,
        )

        cur.execute(
            """DELETE
            FROM user_roles
            WHERE (login, role) IN
                (SELECT login, role
                FROM user_roles
                LEFT JOIN tbl USING(login, role)
                WHERE login=?
                GROUP BY login, role
                HAVING COUNT(tbl.login)=0
                )
            RETURNING *;
        """,
            (userdata["login"],),
        )
        cur.execute("DROP TABLE tbl;")

        cur.executemany(
            """INSERT INTO user_roles(login, role)
            SELECT val.column1 as login, val.column2 as role
            FROM
            (
                VALUES(?, ?)
            ) val
            LEFT JOIN 
                user_roles ON login=val.column1 AND role=val.column2
            WHERE login IS NULL;
        """,
            roles,
        )

        self.connect.commit()

    def delete_user(self, login):
        cur = self.connect.cursor()
        cur.execute("BEGIN;")
        cur.execute(
            """DELETE FROM user_roles
               WHERE login=?;
            """,
            (login,),
        )
        cur.execute(
            """DELETE FROM user
               WHERE login=?;
            """,
            (login,),
        )
        cur.execute("COMMIT;")
        self.connect.commit()
        cur.execute(
            """SELECT * 
            FROM user
            WHERE login=?;
            """,
            (login,),
        )
        return not cur.fetchone()

    def get_roles(self):
        cur = self.connect.cursor()
        cur.execute(
            """SELECT role, descr
            FROM role;"""
        )
        return {key: item for key, item in cur.fetchall()}

    def load_content(self, filter=None):
        content = dict()
        cur = self.connect.cursor()

        if filter:
            filtered_components = list()
            for key, values in filter.items():
                for value in values:
                    filtered_components.append((key, value))

            cur.execute("CREATE TEMPORARY TABLE IF NOT EXISTS tbl3(characteristic, value);")
            cur.executemany(
                """INSERT INTO tbl3(characteristic, value)        
                SELECT val.column1 as characteristic, val.column2 as value
                FROM
                    (
                        VALUES               
                        (?, ?)
                    ) val;
                """,
                tuple(filtered_components),
            )
            cur.execute(
                """SELECT phone_id, model_id, model, price, c1.characteristic, c1.descr, c2.value
                FROM phone
                JOIN model USING(model_id)
                JOIN phone_component USING(phone_id)
                JOIN component c2 USING(component_id)
                JOIN characteristic c1 ON c1.characteristic=c2.characteristic
                WHERE phone_id IN (
                        SELECT ph1.phone_id
                        FROM phone_component ph1
                             JOIN component USING(component_id)
                             JOIN tbl3 USING(characteristic, value)
                        GROUP BY phone_id
                        HAVING COUNT(component_id) = (SELECT COUNT(*)
                                                    FROM phone_component ph2
                                                    WHERE ph2.phone_id = ph1.phone_id)
                      )
                ORDER BY model, price, c1.characteristic;
            """
            )
            records = cur.fetchall()
            cur.execute("DROP TABLE tbl3;")
        else:
            cur.execute(
                """SELECT phone_id, model_id, model, price, c1.characteristic, c1.descr, c2.value
                FROM phone
                JOIN model USING(model_id)
                JOIN phone_component USING(phone_id)
                JOIN component c2 USING(component_id)
                JOIN characteristic c1 ON c1.characteristic=c2.characteristic
                ORDER BY model, price, c1.characteristic;
            """
            )
            records = cur.fetchall()

        for phone_id, model_id, model, price, characteristic, descr, value in records:
            phone = content.setdefault(phone_id, dict())
            phone["modelid"] = model_id
            phone["modelname"] = model
            phone["price"] = price
            components = phone.setdefault("components", dict())
            components[characteristic] = dict()
            components[characteristic]["description"] = descr
            components[characteristic]["value"] = value

        return content

    def add_characteristic(self, content: dict) -> None:
        cur = self.connect.cursor()

        params = tuple(
            (characteristic.strip().lower(), descr.strip())
            for characteristic, descr in content.items()
        )
        cur.executemany(
            """INSERT INTO characteristic(characteristic, descr) 
            SELECT val.column1 as characteristic, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN characteristic ON characteristic=val.column1
            WHERE characteristic IS NULL;    
            """,
            params,
        )
        self.connect.commit()

    def get_characteristics(self):
        cur = self.connect.cursor()
        cur.execute(
            """SELECT characteristic, descr
            FROM characteristic;    
            """
        )
        return {charact: descr for charact, descr in cur.fetchall()}

    def get_component_values(self, characteristic) -> list:
        cur = self.connect.cursor()
        cur.execute(
            """SELECT characteristic, value
            FROM component
            WHERE characteristic=?;    
            """, (characteristic,)
        )
        return [value for _, value in cur.fetchall()]
        

    def get_components(self):
        cur = self.connect.cursor()
        components = dict()
        cur.execute(
            """SELECT characteristic, descr, value
            FROM component
                 JOIN characteristic USING(characteristic);    
            """,
        )
        for characteristic, descr, value in cur.fetchall():
            component = components.setdefault(characteristic, dict())
            component["description"] = descr
            values = component.setdefault("values", list())
            values.append(value)
        return components



    def get_phone_models(self):
        cur = self.connect.cursor()
        cur.execute("""SELECT model_id, model
            FROM model;
        """
        )
        return {key: item for key, item in cur.fetchall()}


    def new_model(self, modelname):
        cur = self.connect.cursor()
        cur.execute("""INSERT INTO model(model)
            SELECT val.column1 as model
            FROM 
                (
                    VALUES (?)
                ) val
                LEFT JOIN model ON val.column1 = model
            WHERE model_id IS NULL
        RETURNING *;
        """, (modelname,)
        )

        fetch = cur.fetchone()
        self.connect.commit()
        return fetch or -1


    def add_or_update_phone(self, content: dict) -> int:
        """
        Inners:
                 content: dict
                    need contains:
                    "phone_id": int - Не обязательный. Если указан, будет проведено обновление записи
                    "model_id": str - Номер модели телефона. Если не указано, то будет поиск по названию модели
                    "modelname": str - Название модели телефона
                    "price": int | float - Цена телефона
                    "components": dict - Параметры телефона:
                        ключ: str - Характеристика
                        значение: dict:
                            "description": str - Описание
                            "value": str - Значение
        Returns: int
                 value of phone_id in database table "phone"
                 or -1 if dublicate
        """
        cur = self.connect.cursor()

        # Добавить отсутствующие конпоненты характеристик телефонов
        components = tuple(
            (characteristic.strip().lower(), value["value"].strip())
            for characteristic, value in content["components"].items()
        )
        cur.executemany(
            """INSERT INTO component(characteristic, value) 
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
            """,
            components
        )
        self.connect.commit()

        if not content.get("model_id"):
            # Добавить отсутствующие модели телефонов если не указан ключ model_id
            model = content["modelname"]
            cur.execute(
                """INSERT INTO model(model) 
                SELECT val.column1 as model
                FROM
                (
                    VALUES (?)
                ) val
                LEFT JOIN
                    model ON val.column1 = model
                WHERE model IS NULL;
                """,
                (model,)
            )
            self.connect.commit()

        # Старт транзакции
        cur.execute("""BEGIN;""")

        if content.get("phone_id"):
            phone_id = content.get("phone_id")
            # Обновить запись телефона
            if content.get("model_id"):
                cur.execute("""UPDATE phone
                    SET model_id = val.column1,
                        price = val.column2
                    FROM
                        (
                            VALUES (?, ?)
                        ) val
                    WHERE phone.phone_id=?;
                    """,
                    (content["model_id"], content["price"], phone_id),
                )
            else:
                cur.execute(
                    """UPDATE phone
                    SET phone.model_id = model.model_id,
                        phone.price = val.column2;
                    FROM
                        (
                            VALUES (?, ?)
                        ) val
                        JOIN model ON val.column1 = model
                    WHERE phone.phone_id=?;
                    """,
                    (content["modelname"], content["price"], phone_id),
                )
        else:
            # Добавить новую запись телефона
            cur.execute(
                """INSERT INTO phone(model_id, price)
                SELECT model_id, val.column2 as price
                FROM
                (
                    VALUES (?, ?)
                ) val
                JOIN model ON val.column1 = model
                RETURNING phone_id;
                """,
                (content["modelname"], content["price"]),
            )
            phone_id = cur.fetchone()[0]


        # Настройка компонентов телефона
        phone_components = tuple(
            (phone_id, characteristic, value) for characteristic, value in components
        )
        # Удалить компоненты, которых больше нет
        if content.get("phone_id"):
            cur.execute("CREATE TEMPORARY TABLE IF NOT EXISTS tbl2(phone_id, component_id);")
            cur.executemany(
                """INSERT INTO tbl2(phone_id, component_id)        
                SELECT val.column1 as phone_id, component_id
                FROM
                    (
                        VALUES               
                        (?, ?, ?)
                    ) val
                    JOIN component ON val.column2=characteristic AND val.column3=value; 
                """,
                phone_components,
            )

            cur.execute(
                """DELETE
                FROM phone_component
                WHERE (phone_id, component_id) IN
                    (SELECT phone_id, component_id
                    FROM phone_component
                    LEFT JOIN tbl2 USING(phone_id, component_id)
                    WHERE phone_id=?
                    GROUP BY phone_id, component_id
                    HAVING COUNT(tbl2.phone_id)=0
                    );
            """,
                (phone_id,),
            )
            cur.execute("DROP TABLE tbl2;")

        # Добавить новые компоненты, если еще отсутствуют конпоненты с аналогичными характеристиками
        cur.executemany(
            """INSERT INTO phone_component(phone_id, component_id, characteristic) 
            SELECT DISTINCT c1.phone_id, c2.component_id, c2.characteristic
            FROM
                (SELECT val.column1 as phone_id, characteristic, val.column3 as value
                    FROM 
                    (
                        VALUES (?, ?, ?)
                    ) val
                    JOIN characteristic ON characteristic=val.column2
                ) c1
                JOIN
                    component c2 ON c1.characteristic = c2.characteristic
                                    AND LOWER(c1.value)=LOWER(c2.value)
                LEFT JOIN phone_component pc ON pc.phone_id=c1.phone_id AND pc.characteristic = c2.characteristic
            WHERE pc.characteristic IS NULL;
            """,
            phone_components,
        )

        # Проверка на дублирование телефона с совпадающими характеристиками
        cur.execute(
            """WITH cte AS
            (
                SELECT model_id, price, component_id
                FROM phone
                JOIN phone_component USING(phone_id)
                WHERE phone_id = ?
            )
            SELECT phone_id
            FROM phone
            JOIN phone_component USING(phone_id)
            WHERE phone_id != ?
                  AND (model_id, price, component_id) IN (SELECT * FROM cte)
            GROUP BY phone_id
            HAVING COUNT(*) = (SELECT COUNT(*) FROM cte);
        """,
            (phone_id, phone_id),
        )

        dublicate_phone_id = cur.fetchone()

        if dublicate_phone_id:
            cur.execute("""ROLLBACK;""")
        else:
            cur.execute("""COMMIT;""")

        self.connect.commit()

        if dublicate_phone_id:
            return -1

        return phone_id

    def delete_phone(self, phone_id):
        cur = self.connect.cursor()
        cur.execute("BEGIN;")
        cur.execute(
            """DELETE
            FROM phone_component
            WHERE phone_id=?;
            """, (phone_id,)
        )
        cur.execute(
            """DELETE
            FROM phone
            WHERE phone_id=?;
            """, (phone_id,)
        )
        cur.execute("COMMIT;")
        self.connect.commit()


    def delete_phones_by_model(self, model_id):
        cur = self.connect.cursor()
        cur.execute("BEGIN;")
        cur.execute(
            """DELETE
            FROM phone_component
            WHERE phone_id IN (
                SELECT phone_id
                FROM phone
                WHERE model_id=?);
            """, (model_id,)
        )
        cur.execute(
            """DELETE
            FROM phone
            WHERE model_id=?;
            """, (model_id,)
        )
        cur.execute(
            """DELETE
            FROM model
            WHERE model_id=?;
            """, (model_id,)
        )
        cur.execute("COMMIT;")
        self.connect.commit()


    def check_or_create_auth_tables(self):
        cur = self.connect.cursor()

        # Если таблица ролей отсутствует, то она будет создана
        cur.execute(
            """CREATE TABLE IF NOT EXISTS role(
            role CHAR(5) PRIMARY KEY NOT NULL,
            descr CHAR(24) NOT NULL);
            """
        )
        self.connect.commit()

        # Если роли пользователя и/или администратора отсутствуют, они будут добавлены
        roles = [
            ("user", "Пользователь"),
            ("admin", "Администратор"),
        ]
        cur.executemany(
            """INSERT INTO role(role, descr) 
            SELECT val.column1 as role, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN role ON role=val.column1
            WHERE role IS NULL;    
            """,
            roles,
        )
        self.connect.commit()

        # Если таблица пользователей отсутствует, то она будет создана
        cur.execute(
            """CREATE TABLE IF NOT EXISTS user(
            login CHAR({login}) PRIMARY KEY NOT NULL,
            password CHAR({password}) NOT NULL,
            firstname CHAR(50),
            secondname CHAR(50),
            patronymic CHAR(50),
            exist BOOLEAN NOT NULL DEFAULT 1);
            """.format(
                login=LOGIN_LENGTH_MAX, password=PASSWORD_LENGTH_MAX
            )
        )
        self.connect.commit()

        # Добавление дефолтной записи администратора, если отсутствует
        users = [
            ("admin", "0000", 1),
        ]
        cur.executemany(
            """INSERT INTO user(login, password, exist) 
            SELECT val.column1 as login, val.column2 as password, val.column3 as exist
            FROM 
            (
                VALUES (?, ?, ?)
            ) val
            LEFT JOIN user ON login=val.column1
            WHERE login IS NULL;    
            """,
            users,
        )
        self.connect.commit()

        # Если таблица сопоставления ролей отсутствует, она будет создана
        cur.execute(
            """CREATE TABLE IF NOT EXISTS user_roles(
            user_roles_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            login CHAR({login}) NOT NULL,
            role CHAR(5) NOT NULL,
            FOREIGN KEY (login) REFERENCES user(login) ON DELETE CASCADE,
            FOREIGN KEY (role) REFERENCES role(role) ON DELETE CASCADE,
            UNIQUE(login, role));
            """.format(
                login=LOGIN_LENGTH_MAX
            )
        )
        self.connect.commit()

        # Добавление прав для записи администратора, если отсутствуют
        alailable_roles = [
            ("admin", "admin"),
            ("admin", "user"),
        ]
        cur.executemany(
            """INSERT INTO user_roles(login, role) 
            SELECT login, role
            FROM
                (SELECT login, role
                FROM 
                (
                    VALUES (?, ?)
                ) val
                JOIN user ON login=val.column1
                JOIN role ON role=val.column2) s
            LEFT JOIN
                user_roles USING(login, role)
            WHERE user_roles_id IS NULL;    
            """,
            alailable_roles,
        )
        self.connect.commit()

        # Всем пользователям без каких-либо ролей проставляем роль user
        user_roles = [
            ("user",),
        ]
        cur.executemany(
            """INSERT INTO user_roles(login, role) 
            SELECT login, s.role
            FROM
                (SELECT login, role
                FROM 
                (
                    VALUES (?)
                ) val
                JOIN role ON role=val.column1
                CROSS JOIN user) s
            LEFT JOIN
                user_roles USING(login)
            WHERE user_roles_id IS NULL;    
            """,
            user_roles,
        )
        self.connect.commit()

    def check_or_create_phone_tables(self):
        cur = self.connect.cursor()

        # Если таблица типов параметров отсутствует, то она будет создана
        cur.execute(
            """CREATE TABLE IF NOT EXISTS characteristic(
            characteristic CHAR(16) PRIMARY KEY NOT NULL,
            descr CHAR(24) NOT NULL);
            """
        )
        self.connect.commit()

        # Если дефолтные типы параметров отсутствуют, они будут добавлены
        params = [
            ("ram", "объем ОЗУ"),
            ("storage", "объем хранилища"),
            ("cpu", "процессор"),
        ]
        cur.executemany(
            """INSERT INTO characteristic(characteristic, descr) 
            SELECT val.column1 as characteristic, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN characteristic ON characteristic=val.column1
            WHERE characteristic IS NULL;    
            """,
            params,
        )
        self.connect.commit()

        # Если таблица компонентов отсутствует, то она будет создана
        cur.execute(
            """CREATE TABLE IF NOT EXISTS component(
            component_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            characteristic CHAR(16) NOT NULL,
            value CHAR(24) NOT NULL,
            FOREIGN KEY (characteristic) REFERENCES characteristic(characteristic),
            UNIQUE(characteristic, value));
            """
        )
        self.connect.commit()

        cur.execute(
            """CREATE TABLE IF NOT EXISTS model(
            model_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            model CHAR(24) NOT NULL UNIQUE);
            """
        )

        # Если таблица телефонов отсутствует, то она будет создана
        cur.execute(
            """CREATE TABLE IF NOT EXISTS phone(
            phone_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            model_id INTEGER,
            price NUMERIC(10.2) NOT NULL,
            FOREIGN KEY (model_id) REFERENCES model(model_id),
            CHECK (price > 0));
            """
        )
        self.connect.commit()

        # Если таблица отсутствует, то она будет создана
        cur.execute(
            """CREATE TABLE IF NOT EXISTS phone_component(
            phone_component_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            phone_id INTEGER NOT NULL,
            component_id INTEGER NOT NULL,
            characteristic CHAR(16) NOT NULL,
            FOREIGN KEY (phone_id) REFERENCES phone(phone_id),
            FOREIGN KEY (component_id) REFERENCES component(component_id),
            UNIQUE(phone_id, characteristic));
            """
        )
        self.connect.commit()
