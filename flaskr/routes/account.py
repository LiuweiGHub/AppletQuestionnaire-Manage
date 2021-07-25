#coding:utf-8
# 认证（登录/注册）路由

from flask import Blueprint, request, render_template, url_for, redirect, send_file
from sqlalchemy.sql import base
from xlsxwriter import Workbook
from models.account import Account, BaseInfo, Record  # 账户模型
from models import db
import time
import io

from flask import Blueprint

account_bp = Blueprint('account', __name__, url_prefix='')


@account_bp.route('/', methods=['GET'])
def getUserInfo():
    data = []
    try:
        account_list = db.session.query(Account).filter(Account.finish_time.isnot(None)).all()
        for account in account_list:
            account = account.to_json()
            account['baseInfo'] = db.session.query(BaseInfo).filter(account['openid'] == BaseInfo.openid).first().to_json()
            account['record'] = db.session.query(Record).filter(account['openid'] == Record.openid).first().to_json()
            data.append(account)
        result = {
            'data': data,
            'sum': len(data)
        }
        return render_template('index.html', result=result) 
    except Exception as e:
        error = f'用户列表错误:{e}'
        return render_template('error.html', result=error) 
        


@account_bp.route('/remove', methods=['POST'])
def post_info():
    try:
        req = request.form
        if 'openid' not in req:
            raise Exception('缺少openid参数')
        openid = req['openid']
        # 方式1: 先查后删除
        record = db.session.query(Record).filter(Record.openid == openid).first()
        baseInfo = db.session.query(BaseInfo).filter(BaseInfo.openid == openid).first()
        account = db.session.query(Account).filter(Account.openid == openid).first()
        if record and baseInfo and account:
            # 删除数据
            db.session.delete(record)
            db.session.commit()
            time.sleep(0.5)
            db.session.delete(baseInfo)
            db.session.commit()
            time.sleep(0.5)
            db.session.delete(account)
            # 提交会话 增删改都要提交会话
            db.session.commit()
        else:
            raise Exception('数据删除失败，未查找到对应信息')
        return redirect(url_for('account.getUserInfo'))
    except Exception as e:
        error = f'删除信息错误:{e}'
        return render_template('error.html', result=error) 

@account_bp.route('/excel', methods=['GET'])
# 导出数据为excel
def get_excel():
    try:
        fp=create_workbook() 
        fp.seek(0)
        return send_file(fp,attachment_filename='调查结果.xlsx',as_attachment=True)
    except Exception as e:
        error = f'导出数据错误:{e}'
        return render_template('error.html', result=error) 
        
def create_workbook():    
    fp=io.BytesIO()
    book=Workbook(fp)
    sheet=book.add_worksheet('数据集合1')

    account_list = db.session.query(Account).filter(Account.finish_time.isnot(None)).all()
    i = 0
    # sheet.write(i, 0, ['昵称', '姓名', '出生日期', '教育背景', '', '完成时间', '注册时间'])
    for account in account_list:
        account = account.to_json()
        baseInfo = db.session.query(BaseInfo).filter(account['openid'] == BaseInfo.openid).first().to_json()
        record = db.session.query(Record).filter(account['openid'] == Record.openid).first().to_json()
        account = list(account.values())
        baseInfo = list(baseInfo.values())
        record = list(record.values())
        
        print(account)
        print(baseInfo)
        print(record)
        values = []
        
        # sheet.write(i, 1, account['nickname'])
        i += 1
    book.close()
    return fp
