from core.settings import LOGIN_LENGTH_MAX, PASSWORD_LENGTH_MAX


class DBManager(object):
    def __init__(self, database):
        self.db = database
        if self.db.db_empty:
            self.create()

    def create(self):
        pass


class AuthDBManager(DBManager):
    def create(self):
        db = self.db

        # Если таблица ролей отсутствует, то она будет создана
        db.execute(
            """CREATE TABLE IF NOT EXISTS role(
            role CHAR(5) PRIMARY KEY NOT NULL,
            descr CHAR(24) NOT NULL);
            """
        )

        # Если роли пользователя и/или администратора отсутствуют, они будут добавлены
        roles = (
            ("user", "Пользователь"),
            ("admin", "Администратор"),
        )
        db.executemany(
            """INSERT INTO role(role, descr) 
            SELECT val.column1 as role, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN role ON role=val.column1
            WHERE role IS NULL;    
            """,
            *roles,
        )

        # Если таблица пользователей отсутствует, то она будет создана
        db.execute(
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

        # Добавление дефолтной записи администратора, если отсутствует
        user = ("admin", "0000", 1)
        db.execute(
            """INSERT INTO user(login, password, exist) 
            SELECT val.column1 as login, val.column2 as password, val.column3 as exist
            FROM 
            (
                VALUES (?, ?, ?)
            ) val
            LEFT JOIN user ON login=val.column1
            WHERE login IS NULL;    
            """,
            *user,
        )

        # Если таблица сопоставления ролей отсутствует, она будет создана
        db.execute(
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

        # Добавление прав для записи администратора, если отсутствуют
        alailable_roles = (
            ("admin", "admin"),
            ("admin", "user"),
        )
        db.executemany(
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
            *alailable_roles,
        )

        # Всем пользователям без каких-либо ролей проставляем роль user
        user_role = "user"
        db.execute(
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
                user_role,
        )
        db.commit()

    def is_free_login(self, login):
        db = self.db
        cursor = db.execute(
            """SELECT login
            FROM user
            WHERE login=?;
        """,
            login,
        )
        return not cursor.fetchone()

    def get_user_list(self):
        db = self.db

        cursor = db.execute(
            """SELECT login, 
                              password, 
                              COALESCE(firstname, '') as firstname, 
                              COALESCE(secondname, '') as secondname, 
                              COALESCE(patronymic, '') as patronymic, 
                              role, 
                              descr, 
                              exist
            FROM user
            JOIN user_roles USING(login)
            JOIN role USING(role)
            ORDER BY exist DESC, login, role;
        """,
        )
        records = cursor.fetchall()

        users = dict()
        for record in records:
            user = users.setdefault(record["login"], dict())
            user["login"] = record["login"]
            user["password"] = record["password"]
            user["firstname"] = record["firstname"]
            user["secondname"] = record["secondname"]
            user["patronymic"] = record["patronymic"]
            role_dict = user.setdefault("role", dict())
            role_dict[record["role"]] = record["descr"]
            user["exist"] = record["exist"]
        return users

    def get_user(self, login):
        db = self.db
        cursor = db.execute(
            """SELECT login, password, 
                              COALESCE(firstname, '') as firstname, 
                              COALESCE(secondname, '') as secondname, 
                              COALESCE(patronymic, '') as patronymic, 
                              role, 
                              descr, 
                              exist
            FROM user
            JOIN user_roles USING(login)
            JOIN role USING(role)
            WHERE login=?;
        """,
            login,
        )
        records = cursor.fetchall()

        user = dict()
        for record in records:
            user["login"] = record["login"]
            user["password"] = record["password"]
            user["firstname"] = record["firstname"]
            user["secondname"] = record["secondname"]
            user["patronymic"] = record["patronymic"]
            role_dict = user.setdefault("role", dict())
            role_dict[record["role"]] = record["descr"]
            user["exist"] = record["exist"]
        return user

    def check_user(self, login: str, password: str) -> dict:
        db = self.db
        cursor = db.execute(
            """SELECT COALESCE(firstname, '') as firstname, 
                              COALESCE(secondname, '') as secondname, 
                              COALESCE(patronymic, '') as patronymic, 
                              role, 
                              descr
            FROM user
            JOIN user_roles USING(login)
            JOIN role USING(role)
            WHERE login=? AND password=? AND exist;
        """,
            login,
            password,
        )
        records = cursor.fetchall()

        roles = dict()
        for record in records:
            role_dict = roles.setdefault(record["role"], dict())
            role_dict["login"] = login
            role_dict["firstname"] = record["firstname"]
            role_dict["secondname"] = record["secondname"]
            role_dict["patronymic"] = record["patronymic"]
            role_dict["role"] = record["role"]
            role_dict["description"] = record["descr"]
        return roles

    def new_user(self, userdata: dict) -> dict:
        db = self.db
        cursor = db.execute(
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
            userdata["login"],
            userdata["password"],
            userdata.get("firstname", ""),
            userdata.get("secondname", ""),
            userdata.get("patronymic", ""),
            userdata.get("exist", 1),
        )
        records = cursor.fetchone()

        if not records:
            return {}

        if roles := userdata.get("roles"):
            newuser = tuple((userdata["login"], role) for role in roles)
        else:
            newuser = ((userdata["login"], "user"),)
        db.executemany(
            """INSERT INTO user_roles(login, role)
            SELECT val.column1 as login, val.column2 as role
            FROM
            (
                VALUES(?, ?)
            ) val;
        """,
            *newuser,
        )
        db.commit()

        return self.check_user(userdata["login"], userdata["password"])

    def update_user(self, userdata: dict):
        db = self.db
        db.execute(
            """UPDATE user
            SET password = ?,
                firstname = ?,
                secondname = ?,
                patronymic = ?,
                exist = ?
            WHERE login=?;
        """,
            userdata["password"],
            userdata.get("firstname", ""),
            userdata.get("secondname", ""),
            userdata.get("patronymic", ""),
            userdata.get("exist", 1),
            userdata["login"],
        )

        roles = tuple((userdata["login"], role) for role in userdata.get("roles"))
        db.execute("CREATE TEMPORARY TABLE IF NOT EXISTS tbl(login, role);")
        db.executemany(
            """INSERT INTO tbl(login, role)        
        SELECT val.column1 as login, val.column2 as role
        FROM
            (
                VALUES               
                (?, ?)
            ) val; 
        """,
            *roles,
        )

        db.execute(
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
            userdata["login"],
        )
        db.execute("DROP TABLE tbl;")

        db.executemany(
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
            *roles,
        )
        db.commit()

    def delete_user(self, login):
        db = self.db

        db.execute("BEGIN;")
        db.execute(
            """DELETE FROM user_roles
               WHERE login=?;
            """,
            login,
        )
        db.execute(
            """DELETE FROM user
               WHERE login=?;
            """,
            login,
        )
        db.execute("COMMIT;")
        db.commit()
        cursor = db.execute(
            """SELECT * 
            FROM user
            WHERE login=?;
            """,
            login,
        )
        return not cursor.fetchone()

    def get_roles(self):
        db = self.db
        cursor = db.execute(
            """SELECT role, descr
            FROM role;"""
        )
        records = cursor.fetchall()
        return dict(records)


class ShopDBManager(DBManager):
    def create(self):
        db = self.db

        # Если таблица типов параметров отсутствует, то она будет создана
        db.execute(
            """CREATE TABLE IF NOT EXISTS characteristic(
            characteristic CHAR(16) PRIMARY KEY NOT NULL,
            descr CHAR(24) NOT NULL);
            """
        )

        # Если дефолтные типы параметров отсутствуют, они будут добавлены
        params = (
            ("ram", "объем ОЗУ"),
            ("storage", "объем хранилища"),
            ("cpu", "процессор"),
        )
        db.executemany(
            """INSERT INTO characteristic(characteristic, descr) 
            SELECT val.column1 as characteristic, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN characteristic ON characteristic=val.column1
            WHERE characteristic IS NULL;    
            """,
            *params,
        )

        # Если таблица компонентов отсутствует, то она будет создана
        db.execute(
            """CREATE TABLE IF NOT EXISTS component(
            component_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            characteristic CHAR(16) NOT NULL,
            value CHAR(24) NOT NULL,
            FOREIGN KEY (characteristic) REFERENCES characteristic(characteristic) ON DELETE CASCADE,
            UNIQUE(characteristic, value));
            """
        )

        # Если таблица моделей отсутствует, то она будет создана
        db.execute(
            """CREATE TABLE IF NOT EXISTS model(
            model_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            model CHAR(24) NOT NULL UNIQUE);
            """
        )

        # Если таблица телефонов отсутствует, то она будет создана
        db.execute(
            """CREATE TABLE IF NOT EXISTS phone(
            phone_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            model_id INTEGER,
            price NUMERIC(10.2) NOT NULL,
            FOREIGN KEY (model_id) REFERENCES model(model_id) ON DELETE CASCADE,
            CHECK (price > 0));
            """
        )

        # Если таблица phone_component отсутствует, то она будет создана
        db.execute(
            """CREATE TABLE IF NOT EXISTS phone_component(
            phone_component_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            phone_id INTEGER NOT NULL,
            component_id INTEGER NOT NULL,
            characteristic CHAR(16) NOT NULL,
            FOREIGN KEY (phone_id) REFERENCES phone(phone_id) ON DELETE CASCADE,
            FOREIGN KEY (component_id) REFERENCES component(component_id) ON DELETE CASCADE,
            FOREIGN KEY (characteristic) REFERENCES characteristic(characteristic) ON DELETE CASCADE,
            UNIQUE(phone_id, characteristic));
            """
        )
        db.commit()

    def load_content(self, filter=None):
        db = self.db
        content = dict()

        if filter:
            filtered_components = list()
            for key, values in filter.items():
                for value in values:
                    filtered_components.append((key, value))

            db.execute(
                "CREATE TEMPORARY TABLE IF NOT EXISTS tbl3(characteristic, value);"
            )
            db.executemany(
                """INSERT INTO tbl3(characteristic, value)        
                SELECT val.column1 as characteristic, val.column2 as value
                FROM
                    (
                        VALUES               
                        (?, ?)
                    ) val;
                """,
                *filtered_components,
            )
            cursor = db.execute(
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
            records = cursor.fetchall()
            db.execute("DROP TABLE tbl3;")
        else:
            cursor = db.execute(
                """SELECT phone_id, model_id, model, price, c1.characteristic, c1.descr, c2.value
                FROM phone
                JOIN model USING(model_id)
                JOIN phone_component USING(phone_id)
                JOIN component c2 USING(component_id)
                JOIN characteristic c1 ON c1.characteristic=c2.characteristic
                ORDER BY model, price, c1.characteristic;
            """
            )
            records = cursor.fetchall()

        for record in records:
            phone = content.setdefault(record["phone_id"], dict())
            phone["modelid"] = record["model_id"]
            phone["modelname"] = record["model"]
            phone["price"] = record["price"]
            components = phone.setdefault("components", dict())
            components[record["characteristic"]] = dict()
            components[record["characteristic"]]["description"] = record["descr"]
            components[record["characteristic"]]["value"] = record["value"]
        return content

    def add_characteristic(self, content: dict) -> None:
        db = self.db

        params = tuple(
            (characteristic.strip().lower(), descr.strip())
            for characteristic, descr in content.items()
        )
        db.executemany(
            """INSERT INTO characteristic(characteristic, descr) 
            SELECT val.column1 as characteristic, val.column2 as descr
            FROM 
            (
                VALUES (?, ?)
            ) val
            LEFT JOIN characteristic ON characteristic=val.column1
            WHERE characteristic IS NULL;    
            """,
            *params,
        )
        db.commit()

    def get_characteristics(self):
        db = self.db
        cursor = db.execute(
            """SELECT characteristic, descr
            FROM characteristic;    
            """
        )
        records = cursor.fetchall()
        return dict(records)

    def get_component_values(self, characteristic) -> list:
        db = self.db
        cursor = db.execute(
            """SELECT characteristic, value
            FROM component
            WHERE characteristic=?;    
            """,
            characteristic,
        )
        records = cursor.fetchall()
        return [record["value"] for record in records]

    def get_components(self):
        db = self.db

        components = dict()
        cursor = db.execute(
            """SELECT characteristic, descr, value
            FROM component
                 JOIN characteristic USING(characteristic);    
            """,
        )
        records = cursor.fetchall()
        for record in records:
            component = components.setdefault(record["characteristic"], dict())
            component["description"] = record["descr"]
            values = component.setdefault("values", list())
            values.append(record["value"])
        return components

    def get_phone_models(self):
        db = self.db

        cursor = db.execute(
            """SELECT model_id, model
            FROM model;
        """
        )
        records = cursor.fetchall()
        return dict(records)

    def new_model(self, modelname):
        db = self.db

        cursor = db.execute(
            """INSERT INTO model(model)
            SELECT val.column1 as model
            FROM 
                (
                    VALUES (?)
                ) val
                LEFT JOIN model ON val.column1 = model
            WHERE model_id IS NULL
        RETURNING *;
        """,
            modelname,
        )
        fetch = cursor.fetchone()
        db.commit()
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
        db = self.db

        # Добавить отсутствующие конпоненты характеристик телефонов
        components = tuple(
            (characteristic.strip().lower(), value["value"].strip())
            for characteristic, value in content["components"].items()
        )
        db.executemany(
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
            *components,
        )

        if not content.get("model_id"):
            # Добавить отсутствующие модели телефонов если не указан ключ model_id
            model = content["modelname"]
            db.execute(
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
                model,
            )
        db.commit()

        # Старт транзакции
        db.execute("BEGIN;")

        if content.get("phone_id"):
            phone_id = content.get("phone_id")
            # Обновить запись телефона
            if content.get("model_id"):
                db.execute(
                    """UPDATE phone
                    SET model_id = val.column1,
                        price = val.column2
                    FROM
                        (
                            VALUES (?, ?)
                        ) val
                    WHERE phone.phone_id=?;
                """,
                    content["model_id"],
                    content["price"],
                    phone_id,
                )
            else:
                db.execute(
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
                    content["modelname"],
                    content["price"],
                    phone_id,
                )
        else:
            # Добавить новую запись телефона
            cursor = db.execute(
                """INSERT INTO phone(model_id, price)
                SELECT model_id, val.column2 as price
                FROM
                (
                    VALUES (?, ?)
                ) val
                JOIN model ON val.column1 = model
                RETURNING phone_id;
                """,
                content["modelname"],
                content["price"],
            )
            phone_id = cursor.fetchone()["phone_id"]

        # Настройка компонентов телефона
        phone_components = tuple(
            (phone_id, characteristic, value) for characteristic, value in components
        )
        # Удалить компоненты, которых больше нет
        if content.get("phone_id"):
            db.execute(
                "CREATE TEMPORARY TABLE IF NOT EXISTS tbl2(phone_id, component_id);"
            )
            db.executemany(
                """INSERT INTO tbl2(phone_id, component_id)        
                SELECT val.column1 as phone_id, component_id
                FROM
                    (
                        VALUES               
                        (?, ?, ?)
                    ) val
                    JOIN component ON val.column2=characteristic AND val.column3=value; 
                """,
                *phone_components,
            )

            db.execute(
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
                phone_id,
            )
            db.execute("DROP TABLE tbl2;")

        # Добавить новые компоненты, если еще отсутствуют конпоненты с аналогичными характеристиками
        db.executemany(
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
            *phone_components,
        )

        # Проверка на дублирование телефона с совпадающими характеристиками
        cursor = db.execute(
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
            phone_id,
            phone_id,
        )

        dublicate_phone_id = cursor.fetchone()

        if dublicate_phone_id:
            db.execute("""ROLLBACK;""")
        else:
            db.execute("COMMIT;")

        db.commit()

        if dublicate_phone_id:
            return -1
        return phone_id

    def delete_phone(self, phone_id):
        db = self.db

        db.execute("BEGIN;")
        db.execute(
            """DELETE
            FROM phone_component
            WHERE phone_id=?;
            """,
            phone_id,
        )
        db.execute(
            """DELETE
            FROM phone
            WHERE phone_id=?;
            """,
            phone_id,
        )
        db.execute("COMMIT;")
        db.commit()

    def delete_phones_by_model(self, model_id):
        db = self.db
        db.execute("BEGIN;")
        db.execute(
            """DELETE
            FROM phone_component
            WHERE phone_id IN (
                SELECT phone_id
                FROM phone
                WHERE model_id=?);
            """,
            model_id,
        )
        db.execute(
            """DELETE
            FROM phone
            WHERE model_id=?;
            """,
            model_id,
        )
        db.execute(
            """DELETE
            FROM model
            WHERE model_id=?;
            """,
            model_id,
        )
        db.execute("COMMIT;")
        db.commit()
