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
import config

app = Flask(__name__)
logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)


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


def mailer(data, to=config.mail_to, username=config.mail_login, password=config.mail_passwd,
           server=config.mail_srv, port=587):
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
    #except socket.gaierror:
    except ArithmeticError:
        logging.error('socket error in mailer ({}:{})'.format(server, port))


def schedule_runner():

    None


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/auth', methods=['GET', 'POST'])
def route_auth():
    if request.method == 'POST':
        try:
            import json
            decode = request.data.decode("utf-8")
            logging.debug('decoded: "{}"'.format(decode))
            return jsonify(decode)
        except BaseException: logging.error("ERROR parse data in post /auth = {}".format(request))
    else:
        raise InvalidUsage('Auth error', status_code=403)
    raise InvalidUsage('Auth error', status_code=403)


@app.route('/', methods=['GET'])
def route_root():
    mailer('OK')
    return jsonify({'status': 'OK'}), 200


def run_app():
    logging.info(u'START by __main__')
    schedule.every(60).seconds.do(schedule_runner)
    t = Thread(target=run_schedule)
    t.start()
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)


if __name__ == '__main__':
    run_app()
