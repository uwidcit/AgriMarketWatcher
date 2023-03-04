import os

from pyfcm import FCMNotification

# Your api-key can be gotten from:
# https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging


def init_push_service():
    push_service = FCMNotification(api_key=os.getenv("FCM_API_KEY"))
    return push_service


def notify(
    content, crop, title="AgriPrice", color="#80", push_service=init_push_service()
):
    topic = change(crop)
    message = {"body": content, "title": title, "icon": "icon", "color": color}
    return push_service.notify_topic_subscribers(
        topic_name=topic,
        message_title=title,
        message_body=content,
        data_message=message,
    )


def change(value):
    return (
        value.replace(" ", "")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
        .lower()
    )


if __name__ == "__main__":
    message_title = "AgriPrice"
    message_body = "Test notification to check logo"
    message_icon = "icon"
    data_message = {
        "body": message_body,
        "title": message_title,
    }
