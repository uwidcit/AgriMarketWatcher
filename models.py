import datetime
from sqlalchemy import DateTime
from log_configuration import logger
from agrinet import db


class DailyCrops(db.Model):
    __tablename__ = 'daily_crops'

    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    unit = db.Column(db.String)
    volume = db.Column(db.REAL)
    price = db.Column(db.REAL)

    date = db.Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_updated = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, commodity, category='', unit='kg', record_date=None, volume=0.0, price=0.0):
        self.commodity = commodity
        self.category = category
        self.unit = unit
        self.volume = volume
        self.price = price
        self.date = record_date

    @classmethod
    def from_dict(cls, record):
        instance = cls(record['commodity'], record['category'], record['unit'])
        instance.volume = record['volume'] if isinstance(record['volume'], float) else 0.0
        instance.price = record['price'] if isinstance(record['price'], float) else 0.0
        instance.date = record['date']  # TODO verify this is correct

        if 'id' in record:
            instance.id = record['id']

        return instance

    def as_dict(self):
        dict_rep = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        dict_rep['date'] = dict_rep['date'].strftime('%Y-%m-%dT%H:%M:%S')
        dict_rep['last_updated'] = dict_rep['last_updated'].strftime('%Y-%m-%dT%H:%M:%S')
        return dict_rep


class MonthlyCrops(db.Model):
    __tablename__ = 'monthly_crops'

    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    unit = db.Column(db.String)
    volume = db.Column(db.REAL)
    min = db.Column(db.REAL)
    max = db.Column(db.REAL)
    mode = db.Column(db.REAL)
    mean = db.Column(db.REAL)

    date = db.Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_updated = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, commodity, category='', unit='kg', record_date=None, volume=0.0, min_val=0.0, max_val=0.0,
                 mode=0.0,
                 mean=0.0):
        self.commodity = commodity
        self.category = category
        self.unit = unit
        self.min = min_val
        self.max = max_val
        self.mode = mode
        self.mean = mean
        self.volume = volume
        self.date = record_date

    @classmethod
    def from_dict(cls, record):
        instance = cls(record['commodity'])
        instance.category = record['category']
        instance.unit = record['unit']
        instance.min = record['min'] if isinstance(record['min'], float) else 0.0
        instance.max = record['max'] if isinstance(record['max'], float) else 0.0
        instance.mode = record['mode'] if isinstance(record['mode'], float) else 0.0
        instance.mean = record['mean'] if isinstance(record['mean'], float) else 0.0
        instance.volume = record['volume'] if isinstance(record['volume'], float) else 0.0

        instance.date = record['date']  # TODO verify this is correct

        if 'id' in record:
            instance.id = record['id']

        return instance

    def as_dict(self):
        dict_rep = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        dict_rep['date'] = dict_rep['date'].strftime('%Y-%m-%dT%H:%M:%S')
        dict_rep['last_updated'] = dict_rep['last_updated'].strftime('%Y-%m-%dT%H:%M:%S')
        return dict_rep


# Needed to re-declare the Recent models as the alembic does not support inheritance
class DailyCropsRecent(db.Model):
    __tablename__ = 'daily_crops_recent'

    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    unit = db.Column(db.String)
    volume = db.Column(db.REAL)
    price = db.Column(db.REAL)

    date = db.Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_updated = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, commodity, category='', unit='kg', record_date=None, volume=0.0, price=0.0):
        self.commodity = commodity
        self.category = category
        self.unit = unit
        self.volume = volume
        self.price = price
        self.date = record_date

    def as_dict(self):
        dict_rep = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        dict_rep['date'] = dict_rep['date'].strftime('%Y-%m-%dT%H:%M:%S')
        dict_rep['last_updated'] = dict_rep['last_updated'].strftime('%Y-%m-%dT%H:%M:%S')
        return dict_rep

    @classmethod
    def from_dict(cls, record):
        instance = cls(record['commodity'])
        instance.category = record['category']
        instance.unit = record['unit']
        instance.volume = record['volume'] if isinstance(record['volume'], float) else 0.0
        instance.price = record['price'] if isinstance(record['price'], float) else 0.0
        instance.date = record['date']  # TODO verify this is correct

        if 'id' in record:
            instance.id = record['id']

        return instance


class MonthlyCropsRecent(db.Model):
    __tablename__ = 'monthly_crops_recent'

    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String, unique=True, nullable=False)
    category = db.Column(db.String)
    unit = db.Column(db.String)
    volume = db.Column(db.REAL)
    min = db.Column(db.REAL)
    max = db.Column(db.REAL)
    mode = db.Column(db.REAL)
    mean = db.Column(db.REAL)

    date = db.Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_updated = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, commodity, category='', unit='kg', record_date=None, volume=0.0, min_val=0.0, max_val=0.0,
                 mode=0.0,
                 mean=0.0):
        self.commodity = commodity
        self.category = category
        self.unit = unit
        self.min = min_val
        self.max = max_val
        self.mode = mode
        self.mean = mean
        self.volume = volume
        self.date = record_date

    @classmethod
    def from_dict(cls, record):
        instance = cls(record['commodity'])
        instance.category = record['category']
        instance.unit = record['unit']
        instance.min = record['min'] if isinstance(record['min'], float) else 0.0
        instance.max = record['max'] if isinstance(record['max'], float) else 0.0
        instance.mode = record['mode'] if isinstance(record['mode'], float) else 0.0
        instance.mean = record['mean'] if isinstance(record['mean'], float) else 0.0
        instance.volume = record['volume'] if isinstance(record['volume'], float) else 0.0

        instance.date = record['date']  # TODO verify this is correct

        if 'id' in record:
            instance.id = record['id']

        return instance

    def as_dict(self):
        dict_rep = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        dict_rep['date'] = dict_rep['date'].strftime('%Y-%m-%dT%H:%M:%S')
        dict_rep['last_updated'] = dict_rep['last_updated'].strftime('%Y-%m-%dT%H:%M:%S')
        return dict_rep


def store_monthly(records):
    length = 0
    try:
        if records:
            for in_record in records:
                db_rec = MonthlyCrops.from_dict(in_record)
                db.session.add(db_rec)
            db.session.commit()
            length = len(records)
    except Exception as e:
        logger.error(e)  # TODO Raise sentry error
        db.session.rollback()
    return length


def get_monthly_by_id(rec_id):
    return db.session.query(MonthlyCrops).get(rec_id)


def get_daily_by_id(rec_id):
    return db.session.query(DailyCrops).get(rec_id)


def store_daily(records):
    length = 0
    try:
        if records:
            for in_record in records:
                db_rec = DailyCrops.from_dict(in_record)
                db.session.add(db_rec)
            db.session.commit()
            length = len(records)
    except Exception as e:
        logger.error(e)  # TODO Raise sentry error
        db.session.rollback()
    return length


def store_most_recent_daily(recent_records):
    length = 0
    try:
        if recent_records and len(recent_records) > 0:
            # drop all the records in the table
            num_rows_deleted = db.session.query(DailyCropsRecent).delete()
            logger.info('Deleted {0} records from the Monthly Crops Recent table'.format(num_rows_deleted))
            for in_record in recent_records:
                db_rec = DailyCropsRecent.from_dict(in_record)
                db.session.add(db_rec)
            db.session.commit()
            length = len(recent_records)
    except Exception as e:
        logger.error(e)  # TODO Raise sentry error
        db.session.rollback()
    return length


def get_distinct_commodity():
    commodities = list(db.session.query(DailyCropsRecent.commodity).distinct())
    return [commodity[0] for commodity in commodities]


def get_distinct_categories():
    categories = list(db.session.query(DailyCropsRecent.category).distinct())
    return [category[0] for category in categories]


def get_distinct_commodity_by_category(category):
    commodities = db.session.query(DailyCropsRecent).filter(DailyCropsRecent.category == category).distinct(
        DailyCropsRecent.commodity)
    return [rec.commodity for rec in commodities]


def get_daily_recent_by_commodity(commodity):
    return db.session.query(DailyCropsRecent.commodity == commodity).one()


def store_most_recent_monthly(recent_records):
    length = 0
    try:
        if recent_records and len(recent_records) > 0:
            # drop all the records in the table
            num_rows_deleted = db.session.query(MonthlyCropsRecent).delete()
            logger.info('Deleted {0} records from the Monthly Crops Recent table'.format(num_rows_deleted))
            for in_record in recent_records:
                db_rec = MonthlyCropsRecent.from_dict(in_record)
                db.session.add(db_rec)
            db.session.commit()
            length = len(recent_records)
    except Exception as e:
        logger.error(e)  # TODO Raise sentry error
        db.session.rollback()
    return length


def get_most_recent_monthly():
    return db.session.query(MonthlyCropsRecent).all()


def get_most_recent_daily():
    return db.session.query(DailyCropsRecent).all()


# ***** FISH ****


class DailyFish(db.Model):
    __tablename__ = 'daily_fish'

    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String, nullable=False)
    unit = db.Column(db.String)
    volume = db.Column(db.REAL)

    min_price = db.Column(db.REAL)
    max_price = db.Column(db.REAL)
    frequent_price = db.Column(db.REAL)
    average_price = db.Column(db.REAL)
    market = db.Column(db.String)

    date = db.Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_updated = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self,
                 commodity,
                 unit='kg',
                 record_date=None,
                 volume=0.0,
                 min_price=0.0,
                 max_price=0.0,
                 frequent_price=0.0,
                 average_price=0.0,
                 market=0.0):
        self.commodity = commodity
        self.unit = unit
        self.volume = volume
        self.min_price = min_price
        self.max_price = max_price
        self.frequent_price = frequent_price
        self.average_price = average_price
        self.market = market
        self.date = record_date

    @classmethod
    def from_dict(cls, record):
        instance = cls(record['commodity'])
        instance.unit = record['unit']
        instance.volume = record['volume'] if isinstance(record['volume'], float) else 0.0
        instance.min_price = record['min_price'] if isinstance(record['min_price'], float) else 0.0
        instance.max_price = record['max_price'] if isinstance(record['max_price'], float) else 0.0
        instance.frequent_price = record['frequent_price'] if isinstance(record['frequent_price'], float) else 0.0
        instance.average_price = record['average_price'] if isinstance(record['average_price'], float) else 0.0
        instance.market = record['market']
        instance.date = record['date']  # TODO verify this is correct

        if 'id' in record:
            instance.id = record['id']

        return instance


class DailyFishRecent(db.Model):
    __tablename__ = 'daily_fish_recent'

    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String, nullable=False)
    unit = db.Column(db.String)
    volume = db.Column(db.REAL)

    min_price = db.Column(db.REAL)
    max_price = db.Column(db.REAL)
    frequent_price = db.Column(db.REAL)
    average_price = db.Column(db.REAL)
    market = db.Column(db.String)

    date = db.Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_updated = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self,
                 commodity,
                 unit='kg',
                 record_date=None,
                 volume=0.0,
                 min_price=0.0,
                 max_price=0.0,
                 frequent_price=0.0,
                 average_price=0.0,
                 market=0.0):
        self.commodity = commodity
        self.unit = unit
        self.volume = volume
        self.min_price = min_price
        self.max_price = max_price
        self.frequent_price = frequent_price
        self.average_price = average_price
        self.market = market
        self.date = record_date

    @classmethod
    def from_dict(cls, record):
        instance = cls(record['commodity'])
        instance.unit = record['unit']
        instance.volume = record['volume'] if isinstance(record['volume'], float) else 0.0
        instance.min_price = record['min_price'] if isinstance(record['min_price'], float) else 0.0
        instance.max_price = record['max_price'] if isinstance(record['max_price'], float) else 0.0
        instance.frequent_price = record['frequent_price'] if isinstance(record['frequent_price'], float) else 0.0
        instance.average_price = record['average_price'] if isinstance(record['average_price'], float) else 0.0
        instance.market = record['market']
        instance.date = record['date']  # TODO verify this is correct

        if 'id' in record:
            instance.id = record['id']

        return instance
