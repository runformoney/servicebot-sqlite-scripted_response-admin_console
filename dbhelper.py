import sqlite3

def db_connect():
    global conn
    conn = sqlite3.connect("servicebot.sqlite")
    return(conn)

class DBHelper:

    def __init__(self, dbname="servicebot.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        print("Connection Successful with DB")
        self.conn.close()

    def setup(self):
        conn = db_connect()
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description varchar(255), owner char(50))"
        tblstmt2 = "CREATE TABLE IF NOT EXISTS cases (ticket_no char(50), log_date char(50), owner char(50), subject char(50), detail varchar(255),assignee char(50), department char(50), owner_fname char(50), owner_lname char(50), owner_phn char(10), owner_email char(50), owner_loc char(10), priority char(2), whd_ticket_id INT)"
        # itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        # ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        tblstmt3 = "CREATE TABLE IF NOT EXISTS admin_cred (owner char(50), password char(15))"
        tbltstmt4 = "INSERT INTO admin_cred (owner,password) VALUES ('503653691', 'Rukhshan@1002')"
        conn.execute(tblstmt)
        conn.execute(tblstmt2)
        conn.execute(tblstmt3)
        # self.conn.execute(itemidx)
        # self.conn.execute(ownidx)
        conn.commit()

    def add_item(self, item_text, owner):
        conn = db_connect()
        owner = str(owner)
        item_text = str(item_text)
        stmt = "INSERT INTO items (description, owner) VALUES (?, ?)"
        args = (item_text, owner)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def get_admin(self,owner):
        stmt = "SELECT * FROM admin_cred WHERE owner = (?)"
        args = (owner,)
        values = [x for x in conn.execute(stmt, args)]
        print("admin: " + str(values))
        return values


    def delete_item(self, item_text, owner):
        owner = str(owner)
        item_text = str(item_text)
        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
        args = (item_text, owner)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def get_items(self, owner):
        conn = db_connect()
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner,)
        return [x[0] for x in conn.execute(stmt, args)]
        #conn.close()

    def delete_chat(self, owner):
        owner = str(owner)
        # stmt = "UPDATE items SET description = '' WHERE owner = (?)"
        stmt = "DELETE FROM items WHERE owner = (?)"
        args = (owner,)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def delete_case(self, ticket_no, owner):
        owner = str(owner)
        ticket_no = str(ticket_no)
        # stmt = "UPDATE items SET description = '' WHERE owner = (?)"
        stmt = "DELETE FROM cases WHERE ticket_no = (?) and owner = (?)"
        args = (ticket_no, owner)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def add_case_subject(self, ticket_no, text, chat, firstName, lastName, date_today):
        #chat = str(chat)
        #ticket_no = str(ticket_no)
        #date_today = str(date_today)
        stmt = "INSERT into cases (ticket_no,log_date, owner, subject, owner_fname, owner_lname) values (?,?,?,?,?,?)"
        args = (ticket_no, date_today, chat, text, firstName, lastName)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def get_case_subject(self, ticket_no, chat, date_today):
        #chat = str(chat)
        #ticket_no = str(ticket_no)
        #date_today = str(date_today)
        stmt = "select * from cases where log_date = (?) and owner = (?) and ticket_no = (?)"
        args = (date_today, chat, ticket_no)
        conn.execute(stmt, args)
        #results = conn.fetchone()
        result = [x for x in conn.execute(stmt, args)]
        # print(result)
        # return results
        return result
        #conn.close()

    def get_case_department(self, ticket_no, chat):
        chat = str(chat)
        ticket_no = str(ticket_no)
        stmt = "select department from cases where owner = (?) and ticket_no = (?)"
        args = (chat, ticket_no)
        conn.execute(stmt, args)
        #result = conn.fetchone()
        result = [x for x in conn.execute(stmt, args)]
        print(result[0][0])
        return result[0][0]
        #conn.close()

    def get_case_whd_ticket_id(self, ticket_no, chat):
        chat = str(chat)
        ticket_no = str(ticket_no)
        stmt = "select whd_ticket_id from cases where owner = (?) and ticket_no = (?)"
        args = (chat, ticket_no)
        conn.execute(stmt, args)
        #results = conn.fetchone()
        # for row in results:
        # return row[0]
        result = [x for x in conn.execute(stmt, args)]
        print(result)
        return result
        #conn.close()

    def delete_invalid_cases(self, chat):
        chat = str(chat)
        stmt = "delete from cases where (subject is NULL or (owner_phn is null and owner_loc is null)) and owner = (?)"
        args = (chat,)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def update_case_detail(self, text, chat, date_today, ticket_no, department):
        #chat = str(chat)
        #ticket_no = str(ticket_no)
        #date_today = str(date_today)
        stmt = "update cases set detail = (?),department = (?) where owner = (?) and log_date = (?) and ticket_no = (?)"
        args = (text, department, chat, date_today, ticket_no)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def update_case_phn_loc(self, phn, loc, chat, date_today, assignee, ticket_no):
        #chat = str(chat)
        #ticket_no = str(ticket_no)
        #date_today = str(date_today)
        #phn = str(phn)
        stmt = "update cases set owner_phn = (?), owner_loc = (?), assignee = (?) where owner = (?) and log_date = (?) and ticket_no = (?)"
        args = (phn, loc, assignee, chat, date_today, ticket_no)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def update_whd_ticket_id(self, whd_ticket_id, owner, date_today, ticket_no):
        owner = str(owner)
        ticket_no = str(ticket_no)
        date_today = str(date_today)
        whd_ticket_id = str(whd_ticket_id)
        stmt = "update cases set whd_ticket_id = (?) where owner = (?) and log_date = (?) and ticket_no = (?)"
        args = (whd_ticket_id, owner, date_today, ticket_no)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()

    def get_pending_case(self, chat):
        chat = str(chat)
        stmt = "select * from cases where owner = (?)"
        args = (chat,)
        conn.execute(stmt, args)
        #results = conn.fetchall()
        #listRes = []
        #for row in results:
            #listRes.append(row)
        #return listRes
        #conn.close()
        result = [x for x in conn.execute(stmt, args)]
        # print(result)
        return result
        #conn.close()

    def update_priority(self, chat, priority, ticket_no):
        #chat = str(chat)
        #priority = str(priority)
        stmt = "update cases set priority = (?) where owner = (?) and ticket_no = (?)"
        args = (priority, chat, ticket_no)
        conn.execute(stmt, args)
        conn.commit()
        #conn.close()
