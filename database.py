import os
import psycopg2


def prepare_record(msg):
    text_list = msg.split('@')

    record_list = []

    for i in text_list[1:]:
        temp_list = i.split(" ")

        userid = temp_list[0]
        writingdate = temp_list[1]
        diary = temp_list[2]

        record = (userid, writingdate, diary)
        record_list.append(record)

    return record_list


# 將資料匯入資料庫
def insert_record(record_list):
    DATABASE_URL = os.environ["DATABASE_URL"]

    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()

    table_columns = "(userid, writingdate, diary)"
    postgres_insert_query = f"""INSERT INTO userdiary {table_columns} VALUES (%s,%s,%s)"""

    try:
        cursor.executemany(postgres_insert_query, record_list)
    except:
        cursor.execute(postgres_insert_query, record_list)

    conn.commit()

    # 要回傳的文字
    message = f"{cursor.rowcount}筆資料成功匯入資料庫囉"

    cursor.close()
    conn.close()

    return message


# 查詢資料
def select_record():
    DATABASE_URL = os.environ["DATABASE_URL"]

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    postgres_select_query = f"""SELECT * FROM userdiary ORDER BY id"""

    cursor.execute(postgres_select_query)
    record = str(cursor.fetchall())

    content = ""
    record = record.split("),")

    for number, r in enumerate(record):
        content += f"第{number + 1}筆資料\n{r}\n"

    cursor.close()
    conn.close()

    return content


# 刪除資料
def delete_record(msg):
    msg = msg.split(" ")[1]
    DATABASE_URL = os.environ["DATABASE_URL"]

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    postgres_delete_query = f"""DELETE FROM userdiary WHERE id = {msg}"""

    cursor.execute(postgres_delete_query)
    conn.commit()

    content = ""

    count = cursor.rowcount
    content += f"{count}筆資料成功從資料庫移除囉"

    cursor.close()
    conn.close()

    return content


# 更新資料
def update_record(msg):
    DATABASE_URL = os.environ["DATABASE_URL"]

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    msg_list = msg.split(" ")
    column = msg_list[1]
    origin = msg_list[2]
    new = msg_list[3]

    postgres_update_query = f"""UPDATE userdiary set {column} = %s WHERE {column} = %s"""

    cursor.execute(postgres_update_query, (new, origin))
    conn.commit()

    content = ""

    count = cursor.rowcount
    content += f"{count}筆資料成功從資料庫更新囉"

    return content
