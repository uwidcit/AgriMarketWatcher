# Send to single device.
from pyfcm import FCMNotification
from firebase import firebase


Firebase =firebase.FirebaseApplication('https://agriprice-6638d.firebaseio.com/')


push_service = FCMNotification(api_key="AAAAJkFqwS4:APA91bE0jE8QTQbQ_3YlnkJSmxpjzS9UmhdpSB6xBAKCl69IgPmoTM8RDsinAXtEzWl1YLnFuN9CYzilDjG219ta3eqTHWa2hfwhh-qfWAt7X-VfsABv__ijIJtVbW4lRHZZUu1g_Zb_")

# # Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

registration_id = "eYH0CLoiw5g:APA91bE44LrODaui02pgZESSD_i4458plbC-5z-PwbcBwPA4fGY3w0pTNfAsPHKfeQmtxmG_5Oyji-Y_4Iq3s747MOpOtpnvPJWm0vNcYCOM9GL4DZhlxrbE9jNpSrnj8HdXjXadVmkb"
message_title = "AgriPrice"
message_body = "Test notification to check logo"
message_icon = "icon"

def notify(message_body1,crop):
	topic = change(crop)
	# result = Firebase.get("/users/"+crop,None)
	# if result:
	# 	for sub in result:
	# 		registration_id =  sub
			# result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body,message_icon=message_icon)
	data_message = {
		# "icon_url": "https://lh3.googleusercontent.com/0H3uJOLZp2VztCX25qA_OBVkJjx2chjTZCA8UM5lHKUhQCEGgjk-2hqHJsUxZpYv7B0W=w300",
		"body":message_body1,
		"title":message_title,
		"icon":"icon",
		"color":"#80"
	}
	result = push_service.notify_topic_subscribers(topic_name = topic,message_title=message_title, message_body=message_body1,data_message=data_message);


def change(value):
	value = value.replace(" ","").replace("(","").replace(")","").replace(".","").replace("'","").lower()
	return value

if __name__ == "__main__":
	# result = Firebase.put("/users/carrot","Subscription",registration_id)
	# Firebase.post("users/carrot","Name","Kerschel")
	# result = Firebase.get("/users/test",None)
	# for sub in result:
		# registration_id =  sub
		# print sub
		# print result[sub]
	# result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body,message_icon=message_icon)
	data_message = {
		# "icon_url": "https://lh3.googleusercontent.com/0H3uJOLZp2VztCX25qA_OBVkJjx2chjTZCA8UM5lHKUhQCEGgjk-2hqHJsUxZpYv7B0W=w300",
		"body":message_body,
		"title":message_title,
	}

	# result = push_service.notify_topic_subscribers(topic_name = 'carrot',message_title=message_title, message_body=message_body,message_icon=message_icon,data_message=data_message,color="#80")

	# print result
	#
