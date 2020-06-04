import json
from random import sample

from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, HiddenField
from wtforms.validators import InputRequired


def load_data(source):
    with open(f"jsons/{source}.json", "r") as f:
        res = json.load(f)
    return res

def save_data(source, obj):
    with open(f"jsons/{source}.json", "w") as f:
        json.dump(obj, f)

days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", \
        "fri": "Пятница", "sat": "Суббота", "sun": "Воскресенье"}

app = Flask(__name__)

@app.route("/")
def render_main():
    goals = load_data("goals")
    all_teachers = load_data("teachers")
    teachers = {k: all_teachers[k] for k in sample(all_teachers.keys(), 6)} 
    return render_template("index.html", goals=goals, teachers=teachers)

@app.route("/goals/<goal>/")
def render_goal(goal):
    goals = load_data("goals")
    all_teachers = load_data("teachers")
    teachers = {}
    for teacher_id in all_teachers:
        if goal in all_teachers[teacher_id]['goals']:
            teachers[teacher_id] = all_teachers[teacher_id]
    return render_template("goal.html", goals=goals, teachers=teachers, goal=goal)

@app.route("/profiles/<id_teacher>/")
def render_teacher(id_teacher):
    try:
        teacher = load_data("teachers")[id_teacher]
        free = load_data("free")[id_teacher]
        goals = load_data("goals")
        return render_template("profile.html", teacher=teacher, id_teacher=id_teacher, free=free, days=days, goals=goals)
    except:
        return "Не могу найти информацию о преподавателе. Вы уверены, что нажали на правильную ссылку?"


class FormRequest(FlaskForm):
    goals = load_data("goals")
    res = []
    for goal in goals:
        res.append((goal, goals[goal]))
    goal = RadioField("Какая цель занятий?", [InputRequired()], choices = res)
    time = RadioField("Сколько времени есть?", [InputRequired()], \
                      choices = [("1-2","1-2 часа в\xa0неделю"), ("3-5","3-5 часов в\xa0неделю"), \
                                 ("5-7","5-7 часов в\xa0неделю"), ("7-10","7-10 часов в\xa0неделю")])
    name = StringField("Вас зовут", [InputRequired()])
    phone = StringField("Ваш телефон", [InputRequired()])


@app.route("/request/")
def render_request():
    form = FormRequest(csrf_enabled=False)
    form.goal.data = sample(form.goal.choices, 1)[0][0]
    form.time.data = sample(form.time.choices, 1)[0][0]
    return render_template("request.html", form=form)

@app.route("/request_done/", methods=["POST"])
def render_request_done():
    form = FormRequest(csrf_enabled=False)
    new_request = {'goal': form.goal.data, 'time': form.time.data, \
                   'name': form.name.data, 'phone': form.phone.data}
    requests = load_data("requests")
    requests.append(new_request)
    save_data("requests", requests)
    return render_template("request_done.html", form=form)


class FormBooking(FlaskForm):
    id_teacher = HiddenField()
    day = HiddenField()
    time = HiddenField()
    name = StringField("Вас зовут", [InputRequired()])
    phone = StringField("Ваш телефон", [InputRequired()])


@app.route("/booking/<id_teacher>/<day>/<time>/")
def render_booking(id_teacher, day, time):
    try:
        teacher = load_data("teachers")[id_teacher]
        free = load_data("free")[id_teacher]
    except:
        return "Преподаватель не найден"
    form = FormBooking(csrf_enabled=False)
    form.id_teacher.data = id_teacher
    form.day.data = day
    form.time.data = time
    flag = False
    try:
        flag = free[day][time]
    except: # время работы, которого вообще нет в словаре
        pass
    return render_template("booking.html", form=form, teacher=teacher, flag=flag, days=days)

@app.route("/booking_done/", methods=["POST"])
def render_booking_done():
    form = FormBooking(csrf_enabled=False)
    try:
        free = load_data("free")
        free_curr = free[form.id_teacher.data]
    except:
        return "Что-то пошло не так - потерялись часы работы преподавателя"
    try:
        flag = free_curr[form.day.data][form.time.data]
    except:
        return "В это время у преподавателя нет урока"
    if flag:
        free[form.id_teacher.data][form.day.data][form.time.data] = False
        save_data("free", free)
        new_booking = {"id_teacher": form.id_teacher.data, "day": form.day.data, \
                       "time": form.time.data, "name": form.name.data, "phone": form.phone.data}
        booking = load_data("booking")
        booking.append(new_booking)
        save_data("booking", booking)
        return render_template("booking_done.html", form=form, days=days) #"заявка отправлена"
    else:
        return "Кто-то уже успел забронировать выбранное вами время." # тут лучше бы специальный шаблон, либо защита от случайного обновления страницы браузера


if __name__ == "__main__":
    app.run() #debug=True)

