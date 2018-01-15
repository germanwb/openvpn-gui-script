import logging
import schedule
import time
import traceback
from threading import Thread
from flask import Flask
from flask import request
from flask import jsonify
from server_meat import InvalidUsage
import os

app = Flask(__name__)

DEFINE_DEFAULT = {
    'mail_to': '',

}


def get_file_dir():
    """get local dir for log and tmp data"""
    import sys
    import os
    _file_url_ = ''
    if sys.platform == 'win32':
        _appdatadir_ = os.getenv('APPDATA')
        if os.path.isdir('{}/openvpn-pygui'.format(_appdatadir_)):
            _file_url_ = '{}/openvpn-pygui'.format(_appdatadir_)
        else:
            os.mkdir("{}/openvpn-pygui".format(_appdatadir_))
            _file_url_ = '{}/openvpn-pygui'.format(_appdatadir_)
    elif sys.platform == 'linux':
        _log_dir_ = '/var/log'
        if os.path.isdir('{}/openvpn-pygui'.format(_log_dir_)):
            _file_url_ = '{}/openvpn-pygui'.format(_log_dir_)
        else:
            os.mkdir("{}/openvpn-pygui".format(_log_dir_))
            _file_url_ = '{}/openvpn-pygui'.format(_log_dir_)
    logging.info("file location = {}".format(_file_url_))
    return _file_url_


def start_ch():

    None


def mailer(data, to=DEFINE_DEFAULT.get('mail_to'), username=DEFINE_DEFAULT.get('mail_login'),
           password=DEFINE_DEFAULT.get('mail_passwd'), server=DEFINE_DEFAULT.get('mail_srv'), port=587):
    import smtplib
    import socket
    hostname = socket.gethostname()
    from email.mime.text import MIMEText
    datamsg = '''{}
    from {}
    '''.format (data, str(hostname))
    msg = MIMEText(datamsg)
    msg['Subject'] = 'OpenVpn PyGui notification'
    msg['From'] = username
    msg['To'] = to
    try:
        s = smtplib.SMTP(server, port)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(username, password)
        s.sendmail(username, to, msg.as_string())
        s.quit()
    except socket.gaierror:
        logging.error('socket error in mailer ({}:{})'.format(server, port))


def schedule_runner():

    None


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


@app.route('/auth', methods=['GET', 'POST'])
def route_auth():
    if request.method == 'POST':
        try:
            import json
            decode = request.data.decode("utf-8")
            print(decode)

        except BaseException: logging.error("ERROR parse data in post /auth = {}".format(decode))
        return jsonify(decode)
    else:
        return InvalidUsage('Auth error', status_code=403)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response



def run_app():
    logging.info(u'START by __main__')
    schedule.every(60).seconds.do(schedule_runner)
    t = Thread(target=run_schedule)
    t.start()
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)


if __name__ == '__main__':
    run_app()
