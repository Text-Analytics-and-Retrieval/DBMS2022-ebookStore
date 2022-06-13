import sqlite3
from link import *
from typing import Optional

class DB():
    def connect():
        cursor = connection.cursor()
        return cursor

    def execute(cursor, sql):
        cursor.execute(sql)
        return cursor

    def execute_input(cursor, sql, input):
        cursor.execute(sql, input)
        return cursor

    def fetchall(cursor):
        return cursor.fetchall()

    def fetchone(cursor):
        return cursor.fetchone()

    def commit():
        connection.commit()

class Member():
    def get_member(account):
        sql = "SELECT ACCOUNT, PASSWORD, MID, IDENTITY, NAME FROM MEMBER WHERE ACCOUNT = ?"
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [account]))
    
    def get_all_account():
        sql = "SELECT ACCOUNT FROM MEMBER"
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def create_member(input):
        sql = "INSERT INTO MEMBER VALUES (null, :name, :account, :password, :identity)"
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()
    
    def delete_product(input):
        sql = 'DELETE FROM RECORD WHERE TNO = ? and PID = ?'
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()
        
    def get_order(userid):
        sql = 'SELECT * FROM ORDER_LIST WHERE MID = ? ORDER BY ORDERTIME DESC'
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [userid]))
    
    def get_role(userid):
        sql = 'SELECT IDENTITY, NAME FROM MEMBER WHERE MID = ?'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [userid]))

class Cart():
    def check(user_id):
        sql = 'SELECT * FROM CART, RECORD WHERE CART.MID = :id AND CART.TNO = RECORD.TNO'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [user_id]))
        
    def get_cart(user_id):
        sql = 'SELECT * FROM CART WHERE MID = ?'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [user_id]))

    def add_cart(input):
        sql = 'INSERT INTO CART VALUES (:aidd, :time, null)'
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()

    def clear_cart(user_id):
        sql = 'DELETE FROM CART WHERE MID = ?'
        DB.execute_input( DB.connect(), sql, [user_id])
        DB.commit()
       
class Product():
    def count():
        sql = 'SELECT COUNT(*) FROM PRODUCT'
        return DB.fetchone(DB.execute( DB.connect(), sql))
    
    def get_product(pid):
        sql ='SELECT * FROM PRODUCT WHERE PID = ?'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [pid]))

    def get_all_product():
        sql = 'SELECT * FROM PRODUCT'
        return DB.fetchall(DB.execute(DB.connect(), sql))
    
    def search(keyword):
        sql = 'SELECT * FROM PRODUCT WHERE PNAME LIKE :search'
        return DB.fetchall(DB.execute_input(DB.connect(), sql, ['%' + keyword + '%']))
    
    def get_name(pid):
        sql = 'SELECT PNAME FROM PRODUCT WHERE PID = ?'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [pid]))[0]

    def add_product(input):
        sql = 'INSERT INTO PRODUCT VALUES (:pid, :name, :price, :category, :description, :filename)'
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()
    
    def delete_product(pid):
        sql = 'DELETE FROM PRODUCT WHERE PID = :id '
        DB.execute_input(DB.connect(), sql, [pid])
        DB.commit()

    def update_product(input):
        sql = 'UPDATE PRODUCT SET PNAME = ?, PRICE = ?, CATEGORY = ?, PDESC = :description WHERE PID = ?'
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()
        
    def update_image(input):
        sql = 'UPDATE PRODUCT SET PIC=:filename WHERE PID=:pid'
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()
    
class Record():
    def get_total_money(tno):
        sql = 'SELECT SUM(TOTAL) FROM RECORD WHERE TNO = ?'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [tno]))[0]

    def check_product(input):
        sql = 'SELECT * FROM RECORD WHERE PID = ? and TNO = ?'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, input))

    def get_price(pid):
        sql = 'SELECT PRICE FROM PRODUCT WHERE PID = :id'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [pid]))[0]

    def add_product(input):
        sql = 'INSERT INTO RECORD VALUES (:id, :tno, 1, :price, :total)'
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()

    def get_record(tno):
        sql = 'SELECT * FROM RECORD WHERE TNO = ?'
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [tno]))

    def get_amount(input):
        sql = 'SELECT AMOUNT FROM RECORD WHERE TNO = ? and PID=:pid'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, input))[0]
    
    def update_product(input):
        sql = 'UPDATE RECORD SET AMOUNT=:amount, TOTAL=:total WHERE PID=:pid and TNO=:tno'
        DB.execute_input(DB.connect(), sql, input)

    def delete_check(pid):
        sql = 'SELECT * FROM RECORD WHERE PID = ?'
        return DB.fetchone(DB.execute_input(DB.connect(), sql, [pid]))

    def get_total(tno):
        sql = 'SELECT SUM(TOTAL) FROM RECORD WHERE TNO = ?'
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [tno]))[0]
    

class Order_List():
    def add_order(input):
        sql = "INSERT INTO ORDER_LIST VALUES (null, :mid, :ordertime, :total, :tno)"
        DB.execute_input(DB.connect(), sql, input)
        DB.commit()

    def get_order():
        sql = 'SELECT OID, NAME, PRICE, ORDERTIME FROM ORDER_LIST NATURAL JOIN MEMBER ORDER BY ORDERTIME DESC'
        return DB.fetchall(DB.execute(DB.connect(), sql))
    
    def get_orderdetail():
        sql = 'SELECT O.OID, P.PNAME, R.SALEPRICE, R.AMOUNT FROM ORDER_LIST O, RECORD R, PRODUCT P WHERE O.TNO = R.TNO AND R.PID = P.PID'
        return DB.fetchall(DB.execute(DB.connect(), sql))


class Analysis():
    def month_price(input):
        sql = "SELECT strftime('%m', ORDERTIME) AS MON, SUM(PRICE) FROM ORDER_LIST WHERE MON = ? GROUP BY MON"
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [input]))

    def month_count(input):
        sql = "SELECT strftime('%m', ORDERTIME) AS MON, COUNT(OID) FROM ORDER_LIST WHERE MON = ? GROUP BY MON"
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [input]))
    
    def category_sale():
        sql = 'SELECT SUM(TOTAL), CATEGORY FROM(SELECT * FROM PRODUCT, RECORD, ORDER_LIST WHERE PRODUCT.PID = RECORD.PID AND RECORD.TNO = ORDER_LIST.TNO) GROUP BY CATEGORY'
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def member_sale(input):
        sql = "SELECT SUM(PRICE), MEMBER.MID, MEMBER.NAME FROM ORDER_LIST, MEMBER WHERE ORDER_LIST.MID = MEMBER.MID AND MEMBER.IDENTITY = ? GROUP BY MEMBER.MID, MEMBER.NAME ORDER BY SUM(PRICE) DESC LIMIT 5"
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [input]))

    def member_sale_count(input):
        sql = "SELECT COUNT(*), MEMBER.MID, MEMBER.NAME FROM ORDER_LIST, MEMBER WHERE ORDER_LIST.MID = MEMBER.MID AND MEMBER.IDENTITY = ? GROUP BY MEMBER.MID, MEMBER.NAME ORDER BY COUNT(*) DESC LIMIT 5"
        return DB.fetchall(DB.execute_input(DB.connect(), sql, [input]))