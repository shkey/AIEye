#!/usr/bin/env python3
from datetime import datetime

from pytz import timezone, utc

from factory import db


cst_tz = timezone('Asia/Shanghai')
utc_tz = timezone('UTC')


class PredictionResult(db.Document):
    path = db.StringField(max_length=255, required=True, unique=True)
    predict_time = db.StringField(max_length=30, required=True)
    category = db.StringField(max_length=30, required=True)
    cataract = db.StringField(max_length=30, required=True)
    normal = db.StringField(max_length=30, required=True)

    def save(self, *args, **kwargs):
        utc_now = datetime.utcnow().replace(tzinfo=utc_tz)
        china_now = utc_now.astimezone(cst_tz)
        self.predict_time = china_now.strftime('%Y-%m-%d %H:%M:%S')

        return super(PredictionResult, self).save(*args, **kwargs)

    def to_dict(self):
        post_dict = {}

        post_dict['path'] = self.path
        post_dict['predict_time'] = self.predict_time
        post_dict['category'] = self.category
        post_dict['cataract'] = self.cataract
        post_dict['normal'] = self.normal

        return post_dict

    def __str__(self):
        return self.to_dict()

    meta = {
        'allow_inheritance': False
    }
