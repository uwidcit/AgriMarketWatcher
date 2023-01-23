def remove_older_than_months(num_months=1):
    from models import delete_crop_records

    print(f"Attempting to remove records older than {num_months} month")
    delete_crop_records()


if __name__ == "__main__":
    num_months = 1
    remove_older_than_months(num_months=num_months)
