from django.shortcuts import render
from datetime import date

data ={'building': [
    {'id':0, 'title':'Главное здание','img_url':'../static/images/gz.png','description':'2-я Бауманская ул., 5, стр. 4'},
    {'id':1, 'title':'Учебно-лабораторный корпус','img_url':'../static/images/ulk_1.png','description':'Рубцовская наб., 2/18'},
    {'id':2, 'title':'Энергомашиностроительный корпус','img_url':'../static/images/energo.jpg','description':'Лефортовская наб., 1'},
    {'id':3, 'title':'Специальное машиностроение','img_url':'../static/images/sm.jpg','description':'Госпитальный пер., 10 '},
    {'id':4, 'title':'Технологический корпус','img_url':'../static/images/ibm.jpg','description':'2-я Бауманская ул., 7 '}
    ]}


def GetDetailedAboutPermit(request, id):
    data_id = data.get('building')[id]
    return render(request, 'bmstu/permit.html', {
        'building': data_id
    })

def FindBuild(request):
    build_name = request.GET.get('q')

    if build_name:
        find = [item for item in data['building'] if build_name.lower() in item['title'].lower()]
    else:
        build_name = ''
        find = data['building']
    return render(request, "bmstu/university.html", {'find': find, 'find_value': build_name})
