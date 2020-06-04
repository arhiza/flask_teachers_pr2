import os
import json
from data import *

if not os.path.exists("jsons"):
    os.mkdir("jsons")

requests = []

with open("jsons/requests.json", "w") as f:
    json.dump(requests, f)

booking = []

with open("jsons/booking.json", "w") as f:
    json.dump(booking, f)

with open("jsons/goals.json", "w") as f:
    json.dump(goals, f) # goals from data.py

teachers_info = {}
teachers_free = {}

for teacher in teachers: # teachers from data.py
    t_free = {}
    for day in teacher["free"]:
        t_free[day] = teacher["free"][day]
    teachers_free[teacher["id"]] = t_free
    t_info = {}
    for key in teacher:
        if not key in ["free", "id"]:
            t_info[key] = teacher[key]
    teachers_info[teacher["id"]] = t_info

with open("jsons/free.json", "w") as f:
    json.dump(teachers_free, f)

with open("jsons/teachers.json", "w") as f:
    json.dump(teachers_info, f)
