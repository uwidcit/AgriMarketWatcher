from models import (
    DailyCrops,
    DailyCropsRecent,
    DailyFish,
    DailyFishRecent,
    MonthlyCrops,
    db,
)


def delete_all_records():
    models = {
        "daily crops": DailyCrops,
        "daily recent crops ": DailyCropsRecent,
        "monthly crops": MonthlyCrops,
        "daily fish": DailyFish,
        "daily recent fish": DailyFishRecent,
    }
    for key, Model in models.items():
        num_records_delete = db.session.query(Model).delete()
        print(f"successfully deleted {num_records_delete} {key} records")

    db.session.commit()
    print("Closed")


if __name__ == "__main__":
    delete_all_records()
