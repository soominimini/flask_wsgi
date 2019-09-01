import GetOldTweets3 as got
import datetime, time
from random import uniform

# 아래는 ibm API
# -*- coding: utf-8 -*-

# import personaliy insights
from builtins import print, range

from watson_developer_cloud import PersonalityInsightsV3
from time import sleep
# from ibm_watson import PersonalityInsightsV3
import json
from openpyxl import load_workbook
import numpy as np

# flask 기반 웹 프로그래밍 라이브러리
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from werkzeug.utils import secure_filename

url = 'https://gateway.watsonplatform.net/personality-insights/api'
apikey = '9aPTQUgHwV74s4gjD7zC4ZsCppop7j1-gNheGmW8S6UA'
service = PersonalityInsightsV3(url=url, iam_apikey=apikey, version='2017-10-13')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


# DB 구조
class User(db.Model):
    id = Column(db.Integer, primary_key=True)
    sns_id = Column(db.VARCHAR(150))  # 연동할 SNS 아이디
    platform_id = Column(db.VARCHAR(150))
    password = Column(db.VARCHAR(150))

    def __init__(self, id=None):
        id = self.id


class Card(db.Model):
    id = Column(db.Integer, primary_key=True)  # 상점 코드로 id를 사용할 것임
    store_type = Column(db.VARCHAR(30))

    def __init__(self, id=None):
        id = self.id


class User_Card(db.Model):
    id = Column(db.Integer, primary_key=True)
    code_store = Column(db.VARCHAR(200))

    def __init__(self, id=None):
        id = self.id


class Data_Ret(db.Model):  # 왓슨의 소비성향 카테고리는(소분류) 42개
    id = Column(db.Integer, primary_key=True)  # 유저의 id
    automobile_ownership_cost = Column(db.Float)
    automobile_safety = Column(db.Float)
    clothes_quality = Column(db.Float)

    def __init__(self, id=None):
        id = self.id


days_range = []

start = datetime.datetime.strptime("2019-01-01", "%Y-%m-%d")
end = datetime.datetime.strptime("2019-02-27", "%Y-%m-%d")
date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]

for date in date_generated:
    days_range.append(date.strftime("%Y-%m-%d"))

print("=== 설정된 트윗 수집 기간은 {} 에서 {} 까지 입니다 ===".format(days_range[0], days_range[-1]))
print("=== 총 {}일 간의 데이터 수집 ===".format(len(days_range)))
# 가져올 트위터의 날짜를 정해주어야 함
# 나는 여기서 2019 01 01 부터 2019 08 27까지 크롤링을 함


# 수집 기간 맞추기
start_date = days_range[0]
end_date = (datetime.datetime.strptime(days_range[-1], "%Y-%m-%d")
            + datetime.timedelta(days=1)).strftime("%Y-%m-%d")  # setUntil이 끝을 포함하지 않으므로, day + 1


@app.route('/', methods=['GET', 'POST'])
def init_page():
    if request.method == 'GET':

        return render_template('index.html')

    elif request.method == 'POST':
        tweet_id = request.form['txtsns']
        platfortm_id = request.form['txtid']
        password = request.form['txtpassword']
        # 프론트 엔드에서 보내는 값을 받음

        # DB에 insert
        user = User()
        user.platform_id = platfortm_id
        user.sns_id = tweet_id
        user.password = password
        db.session.add(user)
        db.session.commit()

        tweetCriteria = got.manager.TweetCriteria().setUsername(tweet_id + "") \
            .setSince(start_date) \
            .setUntil(end_date) \
            .setMaxTweets(-1)
        tweet = got.manager.TweetManager.getTweets(tweetCriteria)

        print("Collecting data start.. from {} to {}".format(days_range[0], days_range[-1]))
        start_time = time.time()

        print("Collecting data end.. {0:0.2f} Minutes".format((time.time() - start_time) / 60))
        print("=== Total num of tweets is {} ===".format(len(tweet)))

        # initialize
        tweet_list = ""

        for i in range(len(tweet)):
            tweet_list += tweet[i].text

        sleep(5)
        # string 결과값 보내기
        profile = service.profile(tweet_list, content_type='text/plain', content_language='ko',
                                  consumption_preferences=True).get_result()

        # 결과값 전체 다 가져오기
        print(json.dumps(profile, indent=5))
        i = 1
        ret = Data_Ret()
        tmp_id = User.query.count()
        ret_category1 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][0]['consumption_preferences']}

        for personality in profile['consumption_preferences'][0]['consumption_preferences']:
            print(i)
            print(personality['score'])

        ret_category2 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][1]['consumption_preferences']}
        ret_category3 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][2]['consumption_preferences']}
        ret_category4 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][3]['consumption_preferences']}
        ret_category5 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][4]['consumption_preferences']}
        ret_category6 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][5]['consumption_preferences']}
        ret_category7 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][6]['consumption_preferences']}
        ret_category8 = {personality['consumption_preference_id']: personality['score'] for personality in
                         profile['consumption_preferences'][7]['consumption_preferences']}
        # 총 8개의 대분류
    #   print(ret_category1)
    #  print(ret_category2)
    # print(ret_category3)


# 시작