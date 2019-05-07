# Send to single device.
from pyfcm import FCMNotification
from firebase import firebase

# Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging
Firebase = firebase.FirebaseApplication('https://agriprice-6638d.firebaseio.com/')
push_service = FCMNotification(
    api_key="AAAAJkFqwS4:APA91bE0jE8QTQbQ_3YlnkJSmxpjzS9UmhdpSB6xBAKCl69IgPmoTM8RDsinAXtEzWl1YLnFuN9CYzilDjG219ta3eqTHWa2hfwhh-qfWAt7X-VfsABv__ijIJtVbW4lRHZZUu1g_Zb_")
registration_id = "eYH0CLoiw5g:APA91bE44LrODaui02pgZESSD_i4458plbC-5z-PwbcBwPA4fGY3w0pTNfAsPHKfeQmtxmG_5Oyji-Y_4Iq3s747MOpOtpnvPJWm0vNcYCOM9GL4DZhlxrbE9jNpSrnj8HdXjXadVmkb"


def notify(content, crop, title="AgriPrice"):
    topic = change(crop)
    message = {
        "body": content,
        "title": title,
        "icon": "icon",
        "color": "#80"
    }
    return push_service.notify_topic_subscribers(topic_name=topic,
                                                 message_title=title,
                                                 message_body=content,
                                                 data_message=message)


def change(value):
    return value.replace(" ", "").replace("(", "").replace(")", "").replace(".", "").replace("'", "").lower()


if __name__ == "__main__":
    message_title = "AgriPrice"
    message_body = "Test notification to check logo"
    message_icon = "icon"
    data_message = {
        "body": message_body,
        "title": message_title,
    }
