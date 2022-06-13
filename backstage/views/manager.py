from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app, flash

UPLOAD_FOLDER = os.path.abspath(os.curdir) + '/static/product/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER']
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        pid = request.values.get('delete')
        data = Record.delete_check(pid)
        
        if(data != None):
            flash('failed')
        else:
            data = Product.get_product(pid)
            image = data[5]
            if(image != None):
                os.remove(os.path.join(config(), image))
                
            Product.delete_product(pid)
    
    elif 'edit' in request.values:
        pid = request.values.get('edit')
        return redirect(url_for('manager.edit', pid=pid))
    
    book_data = book()
    return render_template('productManager.html', book_data = book_data, user=current_user.name)

def book():
    book_row = Product.get_all_product()
    book_data = []
    for i in book_row:
        book = {
            '商品編號': i[0],
            '商品名稱': i[1],
            '商品售價': i[2],
            '商品類別': i[3]
        }
        book_data.append(book)
    return book_data

@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while(data != None):
            number = str(random.randrange( 10000, 99999))
            en = random.choice(string.ascii_letters)
            pid = en + number
            data = Product.get_product(pid)

        name = request.values.get('name')
        price = request.values.get('price')
        category = request.values.get('category')
        description = request.values.get('description')
        file = request.files['file']
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(config(), filename))
        
        pic = pid + filename[filename.index("."):]
        os.chdir(config())
        os.rename(filename, pic)

        if (len(name) < 1 or len(price) < 1):
            return redirect(url_for('manager.productManager'))
        
        Product.add_product(
            {'pid' : pid,
             'name' : name,
             'price' : price,
             'category' : category,
             'description':description,
             'filename':pic
            }
        )

        return redirect(url_for('manager.productManager'))

    return redirect(url_for('manager.productManager'))

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))

    if request.method == 'POST':

        new_file = request.files['file']
        pid = request.values.get('pid')
        pname = request.values.get('name')
        price = request.values.get('price')
        category = request.values.get('category')
        description = request.values.get('description')
        
        if new_file:
            data = Product.get_product(pid)
            image = data[5]
            if image:
                os.remove(os.path.join(config(), image))
            
            filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(config(), filename))
            pic = pid + filename[filename.index("."):]
            os.chdir(config())
            os.rename(filename, pic)
            
            input = (pname, price, category, description, pid)
            Product.update_product(input)
            
            img = (pic, pid)
            Product.update_image(img)
        
        else:
            input = (pname, price, category, description, pid)
            Product.update_product(input)
        
        return redirect(url_for('manager.productManager'))

    else:
        product = show_info()
        return render_template('edit.html', data=product)


def show_info():
    pid = request.args['pid']
    data = Product.get_product(pid)
    pname = data[1]
    price = data[2]
    category = data[3]
    description = data[4]
    image = data[5]

    product = {
        '商品編號': pid,
        '商品名稱': pname,
        '單價': price,
        '類別': category,
        '商品敘述': description,
        '商品圖片': image
    }
    return product


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_order()
        order_data = []
        for i in order_row:
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單總價': i[2],
                '訂單時間': i[3]
            }
            order_data.append(order)
            
        orderdetail_row = Order_List.get_orderdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3]
            }
            order_detail.append(orderdetail)

    return render_template('orderManager.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)