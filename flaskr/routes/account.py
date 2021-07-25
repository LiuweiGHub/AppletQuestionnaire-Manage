#coding:utf-8
# 认证（登录/注册）路由

import re
from flask import Blueprint, request, render_template
from models.account import Account, BaseInfo, Record  # 账户模型
from models import db
from utils import resp
import time

from flask import Blueprint

account_bp = Blueprint('account', __name__, url_prefix='')


@account_bp.route('/list', methods=['GET'])
def getUserInfo():
    result = []
    try:
        account_list = db.session.query(Account).all()
        for account in account_list:
            account = account.to_json()
            account['baseInfo'] = db.session.query(BaseInfo).filter(account['openid'] == BaseInfo.openid).first().to_json()
            account['record'] = db.session.query(Record).filter(account['openid'] == Record.openid).first().to_json()
            result.append(account)
    except Exception as e:
        result = []
    finally:
        return render_template('index.html', result=result) 


@account_bp.route('/remove', methods=['GET'])
def post_info():
    result = {'code': 200, 'msg': 'ok', 'data': {}}
    try:
        req = request.args
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
            time.sleep(0.5)
            db.session.delete(baseInfo)
            time.sleep(0.5)
            db.session.delete(account)
            # 提交会话 增删改都要提交会话
            db.session.commit()
        else:
            raise Exception('数据删除失败，未查找到对应信息')
    except Exception as e:
        result['code'] = 500
        result['msg'] = f'删除信息错误:{e}'
    finally:
        return resp(result['code'], result['msg'], result['data'])



