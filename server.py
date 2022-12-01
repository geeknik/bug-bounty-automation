import os
import sys
import base64
import json
import subprocess
import sqlite3

from flask import Flask
from flask import request
from flask import g

app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        domain_name = request.json['domain']
        domain_name = domain_name.lower()
        if not os.path.exists('results'):
            subprocess.check_output('mkdir results', shell = True)
        subprocess.check_output('mkdir results/' + domain_name, shell = True)
        subprocess.check_output('subfinder -d ' + domain_name + ' -o results/' + domain_name + '/subfinder.txt', shell = True)
        subprocess.check_output('dnsx -l results/' + domain_name + '/subfinder.txt -o results/' + domain_name + '/dnsx.txt', shell = True)
        subprocess.check_output('httpx -l results/' + domain_name + '/dnsx.txt -o results/' + domain_name + '/httpx.txt', shell = True)
        subprocess.check_output('nuclei -l results/' + domain_name + '/httpx.txt -o results/' + domain_name + '/nuclei.txt', shell = True)
        with app.app_context():
            conn = get_db()
            conn.execute('CREATE TABLE IF NOT EXISTS results (domain_name VARCHAR, subfinder VARCHAR, dnsx VARCHAR, httpx VARCHAR, nuclei VARCHAR)')
            subfinder = open('results/' + domain_name + '/subfinder.txt', 'r')
            dnsx = open('results/' + domain_name + '/dnsx.txt', 'r')
            httpx = open('results/' + domain_name + '/httpx.txt', 'r')
            nuclei = open('results/' + domain_name + '/nuclei.txt', 'r')
            conn.execute('INSERT INTO results (domain_name, subfinder, dnsx, httpx, nuclei) VALUES (?, ?, ?, ?, ?)', [domain_name, subfinder.read(), dnsx.read(), httpx.read(), nuclei.read()])
            conn.commit()
        return json.dumps({'domain' : domain_name})
    return "Hello, World!"

@app.route('/results', methods = ['GET'])
def results():
    with app.app_context():
        conn = get_db()
        cur = conn.execute('SELECT domain_name, subfinder, dnsx, httpx, nuclei FROM results')
        domains = []
        for row in cur.fetchall():
            domains.append(dict(domain_name = row[0],
                subfinder = '<br>'.join(['<span style="color: red">' + x + '</span>' if x in row[3].split('\n') else '<span style="color: blue">' + x + '</span>' if x in row[2].split('\n') else x for x in row[1].split('\n')]),
                dnsx = '<br>'.join(['<span style="color: red">' + x + '</span>' if x in row[3].split('\n') else '<span style="color: blue">' + x + '</span>' if x in row[2].split('\n') else x for x in row[2].split('\n')]),
                httpx = '<br>'.join(['<span style="color: red">' + x + '</span>' if x in row[3].split('\n') else '<span style="color: blue">' + x + '</span>' if x in row[2].split('\n') else x for x in row[3].split('\n')]),
                nuclei = '<br>'.join(['<span style="color: red">' + x + '</span>' if x in row[3].split('\n') else '<span style="color: blue">' + x + '</span>' if x in row[2].split('\n') else x for x in row[4].split('\n')])
            ))
        return json.dumps(domains)

@app.route('/results/<string:domain_name>', methods = ['GET'])
def results_per_domain(domain_name):
    with app.app_context():
        conn = get_db()
        cur = conn.execute('SELECT domain_name, subfinder, dnsx, httpx, nuclei FROM results WHERE domain_name = ?', [domain_name])
        row = cur.fetchone()
        domain = dict(domain_name = row[0], subfinder = row[1].split('\n'), dnsx = row[2].split('\n'), httpx = row[3].split('\n'), nuclei = row[4].split('\n'))
        return json.dumps(domain)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug='True',port='5002')
