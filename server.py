#from pandas import Timedelta
from flask import Flask, session, redirect, url_for, request, render_template, jsonify
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import os, random
from typing import Set
from datetime import datetime
from collections import Counter, defaultdict
from dataclasses import dataclass, field

# see dataset.py
import dataset

#start_time = datetime.now()
x = 5

DATASET = dataset.load_examples()
app = Flask(__name__)
if app.debug:
    app.config.update({
        'SECRET_KEY': 'Just in Debug Mode!'
    })
else:
    app.config.update({
        'SECRET_KEY': os.urandom(24)
    })
engine = create_engine('sqlite:///labels.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Label(Base):
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True)
    when = Column(DateTime)
    #how_long = Column(String)
    what = Column(String)
    who = Column(String)
    label = Column(String)

Base.metadata.create_all(engine)

def get_user():
    if 'user' not in session:
        return None
    return session['user']

def redirect_login():
    return redirect(url_for('login', destination=request.full_path))

@app.route('/')
def front_page():
    user = get_user()
    if user is None:
        return redirect_login()
    next_id = random.choice(list(DATASET.keys()))
    return redirect(url_for('label', id=next_id))

def process_label(label: str) -> str:
    return label.upper().replace(' ', '_').replace('-', '_')

@app.route("/label/<id>")
def label(id: str):
    user = get_user()
    if user is None:
        return redirect_login()
    example = DATASET[id]
    labels = []
    db = Session()
    for (lbl,) in db.query(Label.label).filter(Label.who==user, Label.what==id):
        labels.append(lbl)
    print(labels)
    db.close()
    add_buttons = []
    delete_buttons = []
    for button in dataset.DEFAULT_BUTTONS:
        as_lbl = process_label(button)
        '''
        if as_lbl in labels:
            delete_buttons.append(as_lbl)
            labels.remove(as_lbl)
        else:
            add_buttons.append(as_lbl)
        '''
        add_buttons.append(as_lbl)
    '''
    for lbl in labels:
        delete_buttons.append(lbl)
    '''
    start_time = datetime.now()
    print("this is the id " + str(datetime.now()))
    #'timestamp' below is not being represented as datetime.datetime value but instead is being shown as a simple string stripped down
    return render_template('label_one.j2', example=example, add_buttons=add_buttons, delete_buttons=delete_buttons, timestamp=datetime.now())

@app.route("/form/label", methods=["POST"])
def post_label():
    user = get_user()
    if user is None:
        return redirect_login()
    id = request.form['id']
    assert(id in DATASET)
    db = Session()
    #timedelta = str(datetime.now() - request.form['start_time'])
    print(request.form['start_time'])
    #print(str(datetime.now() - request.form['start_time']))
    print(str(x + 1))
    #print(str(user) + "took" + str(timedelta) + "to label this one"
    #label = Label(who=user, when=datetime.now(), how_long=timedelta, what=id, label=process_label(request.form['label']))
    label = Label(who=user, when=datetime.now(), what=id, label=process_label(request.form['label']))
    db.add(label)
    db.commit()
    db.close()
    next_id = random.choice(list(DATASET.keys()))
    return redirect(url_for('label', id=next_id))

@app.route("/form/undo_label", methods=["POST"])
def undo_label():
    user = get_user()
    if user is None:
        return redirect_login()
    id = request.form['id']
    assert(id in DATASET)
    db = Session()
    for (row_id,) in db.query(Label.id).filter(Label.who==user, Label.what==id, Label.label==process_label(request.form['label'])):
        row = db.query(Label).get(row_id)
        print("DELETE: ", row)
        db.delete(row)
    db.commit()
    db.close()
    return redirect(url_for('label', id=id))

@dataclass
class LabelStats:
    label: str
    instances: Set[int] = field(default_factory=set)
    users: Set[str] = field(default_factory=set)

@app.route("/stats")
def stats():
    user = get_user()
    if user is None:
        return redirect_login()

    label_stats = {}
    db = Session()
    for label in db.query(Label):
        if label.label not in label_stats:
            label_stats[label.label] = LabelStats(label.label)
        stats = label_stats[label.label]
        stats.instances.add(label.what)
        stats.users.add(label.who)

    db.close()
    return render_template('stats.j2', label_stats=label_stats, len=len)

@app.route("/labels.json")
def download_json():
    data = []
    db = Session()
    for label in db.query(Label):
        data.append({'user': label.who, 'target': label.what, 'label': label.label, 'when': label.when})
    return jsonify(data)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.j2', destination=request.args.get('destination', '/'), suggested_random=random.randint(0,100_000))
    else:
        session['user'] = request.form['user']
        return redirect(request.form.get('destination', '/'))

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/login')
