import re, math, random, string
from typing_extensions import Self
from flask import Flask, request, render_template, template_rendered, Blueprint, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
from sqlalchemy import null
from link import *
from api.sql import Member, Order_List, Product, Record, Cart

store = Blueprint('bookstore', __name__, template_folder='../templates')

@store.route('/', methods=['GET', 'POST'])
@login_required
def bookstore():
    maximum = 9
    result = Product.count()
    pagenum = math.ceil(result[0]/9)
    page = 1
    param = 0
    endpoint = 0
    if request.method == 'GET':
        if(current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('index'))

    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        flag = 1
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        search = request.values.get('keyword')
        keyword = search
        
        book_row = Product.search(keyword)
        book_data = []
        final_data = []
        
        for i in book_row:
            book = {
                '商品編號': i[0],
                '商品名稱': i[1],
                '商品價格': i[2]
            }
            book_data.append(book)
            total = total + 1
        
        if(len(book_data) < end):
            end = len(book_data)
            endpoint = 1
            
        for j in range(start, end):
            final_data.append(book_data[j])
            
        pagenum = math.ceil(total/9)
        
        return render_template('bookstore.html', flag=flag, keyword=search, book_data=final_data, user=current_user.name, page=page, endpoint=endpoint, pagenum=pagenum)    
        
    elif 'keyword' in request.args:
        flag = 1
        search = request.values.get('keyword')
        keyword = search
        book_row = Product.search(keyword)
        book_data = []
        final_data = []
        total = 0
        
        for i in book_row:
            book = {
                '商品編號': i[0],
                '商品名稱': i[1],
                '商品價格': i[2]
            }

            book_data.append(book)
            total = total + 1

        if len(book_data) < maximum:
            endpoint = 1
        
        pagenum = math.ceil(total/9)   
        
        for i in book_row:
            book = {
                '商品編號': i[0],
                '商品名稱': i[1],
                '商品價格': i[2]
            }
            if len(final_data) < maximum:
                final_data.append(book)
        
        
        return render_template('bookstore.html', keyword=search, flag=flag, book_data=final_data, user=current_user.name, page=page, endpoint=endpoint, pagenum=pagenum)    
    
    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        
        book_row = Product.get_all_product()
        book_data = []
        final_data = []
        
        for i in book_row:
            pid = i[0]
            pname = i[1]
            price = i[2]
            
            book = {
                '商品編號': pid,
                '商品名稱': pname,
                '商品價格': price
            }
            book_data.append(book)
            
        if(len(book_data) < end):
            end = len(book_data)
            endpoint = 1
            
        for j in range(start, end):
            final_data.append(book_data[j])
        
        return render_template('bookstore.html', book_data=final_data, user=current_user.name, page=page, endpoint=endpoint, pagenum=pagenum)    

    elif 'pid' in request.args:
        pid = request.args['pid']
        data = Product.get_product(pid)
        
        pname = data[1]
        price = data[2]
        category = data[3]
        description = data[4]
        image = data[5]
        
        if image == None:
            image = 'sdg.jpg'
        
        product = {
            '商品編號': pid,
            '商品名稱': pname,
            '單價': price,
            '類別': category,
            '商品敘述': description,
            '商品圖片': image
        }

        return render_template('product.html', data = product)
      
    else:
        book_row = Product.get_all_product()
        book_data = []
        for i in book_row:
            pid = i[0]
            pname = i[1]
            price = i[2]
            pic = i[5]
            
            book = {
                '商品編號': pid,
                '商品名稱': pname,
                '商品價格': price,
                '商品圖片': pic
            }
            if len(book_data) < maximum:
                book_data.append(book)
        
        return render_template('bookstore.html', book_data=book_data, user=current_user.name, page=page, endpoint=endpoint, pagenum=pagenum)

# 會員購物車
@store.route('/cart', methods=['GET', 'POST'])
@login_required # 使用者登入後才可以看
def cart():

    # 以防管理者誤闖
    if request.method == 'GET':
        if( current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('index'))

    # 回傳有 pid 代表要 加商品
    if request.method == 'POST':
        
        if "pid" in request.form :
            data = Cart.get_cart(current_user.id)
            
            if(data == None): #假如購物車裡面沒有他的資料
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                input = { 
                    'aidd': 1, 
                    'time': time
                }
                Cart.add_cart(input) # 幫他加一台購物車
                data = Cart.get_cart(current_user.id) 
                
            tno = data[2] # 取得交易編號
            pid = request.values.get('pid') # 使用者想要購買的東西
            # 檢查購物車裡面有沒有商品
            input = (pid, tno)
            
            product = Record.check_product(input)
            # 取得商品價錢
            price = Product.get_product(pid)[2]

            # 如果購物車裡面沒有的話 把他加一個進去
            if(product == None):
                Record.add_product( {'id': tno, 'tno':pid, 'price':price, 'total':price} )
            else:
                # 假如購物車裡面有的話，就多加一個進去
                input = (tno, pid)
                amount = Record.get_amount(input)
                total = (amount+1) * int(price)
                Record.update_product({'amount':amount+1, 'tno':tno , 'pid':pid, 'total':total})

        elif "delete" in request.form :
            pid = request.values.get('delete')
            tno = Cart.get_cart(current_user.id)[2]
            input = (tno, pid)
            Member.delete_product(input)
            product_data = only_cart()
        
        elif "user_edit" in request.form:
            change_order()  
            return redirect(url_for('bookstore.bookstore'))
        
        elif "buy" in request.form:
            change_order()
            return redirect(url_for('bookstore.order'))

        elif "order" in request.form:
            tno = Cart.get_cart(current_user.id)[2]
            total = Record.get_total_money(tno)
            Cart.clear_cart(current_user.id)

            time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            input = (current_user.id, time, total, tno)
            Order_List.add_order(input)

            return render_template('complete.html', user=current_user.name)

    product_data = only_cart()
    
    if product_data == 0:
        return render_template('empty.html', user=current_user.name)
    else:
        return render_template('cart.html', data=product_data, user=current_user.name)

@store.route('/order')
def order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]

    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pname = Product.get_name(i[1])
        product = {
            '商品編號': i[1],
            '商品名稱': pname,
            '商品價格': i[3],
            '數量': i[2]
        }
        product_data.append(product)
    
    total = Record.get_total(tno)[0]

    return render_template('order.html', data=product_data, total=total, user=current_user.name)

@store.route('/orderlist')
def orderlist():
    if "oid" in request.args :
        pass
    
    user_id = current_user.id

    data = Member.get_order(user_id)
    orderlist = []

    for i in data:
        temp = {
            '訂單編號': i[0],
            '訂單總價': i[3],
            '訂單時間': i[2]
        }
        orderlist.append(temp)
    
    orderdetail_row = Order_List.get_orderdetail()
    orderdetail = []

    for j in orderdetail_row:
        temp = {
            '訂單編號': j[0],
            '商品名稱': j[1],
            '商品單價': j[2],
            '訂購數量': j[3]
        }
        orderdetail.append(temp)


    return render_template('orderlist.html', data=orderlist, detail=orderdetail, user=current_user.name)

def change_order():
    data = Cart.get_cart(current_user.id)
    tno = data[2] # 使用者有購物車了，購物車的交易編號是什麼
    product_row = Record.get_record(data[2])

    for i in product_row:
        
        # i[0]：交易編號 / i[1]：商品編號 / i[2]：數量 / i[3]：價格
        if int(request.form[i[1]]) != i[2]:
            Record.update_product({
                'amount':request.form[i[1]],
                'pid':i[1],
                'tno':tno,
                'total':int(request.form[i[1]])*int(i[3])
            })
            print('change')

    return 0


def only_cart():
    
    count = Cart.check(current_user.id)

    if(count == None):
        return 0
    
    data = Cart.get_cart(current_user.id)
    tno = data[2]
    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pid = i[1]
        pname = Product.get_name(i[1])
        price = i[3]
        amount = i[2]
        
        product = {
            '商品編號': pid,
            '商品名稱': pname,
            '商品價格': price,
            '數量': amount
        }
        product_data.append(product)
    
    return product_data