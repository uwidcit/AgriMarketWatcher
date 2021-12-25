from models import (
    db,
    DailyCrops,
    DailyCropsRecent,
    MonthlyCrops,
    DailyFish,
    DailyFishRecent,
)

from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def remove_older_than_months(num_months=1):
    models = {
        DailyCrops: DailyCrops.date,
        DailyCropsRecent: DailyCropsRecent.date,
        MonthlyCrops: MonthlyCrops.date,
        DailyFish: DailyFish.date,
        DailyFishRecent: DailyFishRecent.date,
    }

    months_before = date.today() + relativedelta(months=-num_months)
    dt_delta = datetime(months_before.year, months_before.month, months_before.day)

    for Model, date_field in models.items():
        db.session.query(Model).filter(date_field > dt_delta).delete()

    db.session.commit()
    print(f"Successfully removed records older than {num_months}")


if __name__ == "__main__":
    num_months = 1
    print(f"Attempting to remove records older than {num_months} month")
    remove_older_than_months(num_months=num_months)
