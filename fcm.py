# Send to single device.
from pyfcm import FCMNotification
from firebase_token import firebase
from firebase import firebase


Firebase =firebase.FirebaseApplication('https://agriprice-6638d.firebaseio.com/')


push_service = FCMNotification(api_key="AAAAJkFqwS4:APA91bHWbSUhyDuBx2XUC4o1hmzYA3gVgF3lCaj72F0LEnzBxa6Q5NlLLzCk-QXVojFnOV8HxY6_41jtV2GDRXEH51SXgQyI56gpIvZexjiKQtUUJ6Nh0648H4j8asxmiUsYBpwi7-0Ccd_pluLa0N9ebAd-EzLxcA")

# # Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

registration_id = "fRgM9BzGbws:APA91bFPpSymXODqrqhpni_5VX3VYgVymBytzNTTfNeRVoKeurZk4YOgKbCrygWXL-oc_PFT8VqE7YDc5F9muJsjOsrgfSocjOxq6CW2S3vqg1izmRUnPM6G1pKkiPl1pNomUaHC0MCX"
message_title = "AgrineTT"
message_body = "CROPS"
message_icon = "http://sta.uwi.edu/rdifund/projects/agrinett/img/agriLogo2.png"


def notify(message_body,crop):
	message_body = message_body
	result = Firebase.get("/users/"+crop,None)
	if result:
		for sub in result:
			registration_id =  sub
			result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body,message_icon=message_icon)





if __name__ == "__main__":
	result =Firebase.put("/users/carrot","Subscription",registration_id)
	# Firebase.post("users/carrot","Name","Kerschel")
	result = Firebase.get("/users/test",None)
	for sub in result:
		# registration_id =  sub
		# print sub
		print result[sub]
		# result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body,message_icon=message_icon)
		# print result
	#
