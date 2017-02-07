# Send to single device.
from pyfcm import FCMNotification
from firebase_token import firebase
from firebase import firebase


Firebase =firebase.FirebaseApplication('https://agriprice-6638d.firebaseio.com/')
# registration_ids = "fQBmfDmg69s:APA91bGb8oLZd4RewFESwvLQfSE8OrI710YhG-0_WHxkYmkv1MlWFyNcZudhYXXOEFVppdMvIhr8MoxiE6vd_GZecPCOOIaDfeKFDa5deGxxUht0bkXigRAlvCOvzCQryUiwLXw6r4-q,fQBmfDmg69s:APA91bGb8oLZd4RewFESwvLQfSE8OrI710YhG-0_WHxkYmkv1MlWFyNcZudhYXXOEFVppdMvIhr8MoxiE6vd_GZecPCOOIaDfeKFDa5deGxxUht0bkXigRAlvCOvzCQryUiwLXw6r4-q]"
# result = firebase.get('/users', None, {'print': 'pretty'})
# print result
# {'error': 'Permission denied.'}

push_service = FCMNotification(api_key="AAAAJkFqwS4:APA91bHWbSUhyDuBx2XUC4o1hmzYA3gVgF3lCaj72F0LEnzBxa6Q5NlLLzCk-QXVojFnOV8HxY6_41jtV2GDRXEH51SXgQyI56gpIvZexjiKQtUUJ6Nh0648H4j8asxmiUsYBpwi7-0Ccd_pluLa0N9ebAd-EzLxcA")

# # Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

registration_id = "fRgM9BzGbws:APA91bFPpSymXODqrqhpni_5VX3VYgVymBytzNTTfNeRVoKeurZk4YOgKbCrygWXL-oc_PFT8VqE7YDc5F9muJsjOsrgfSocjOxq6CW2S3vqg1izmRUnPM6G1pKkiPl1pNomUaHC0MCX"
message_title = "AgrineTT"
message_body = "CROPS"
message_icon = "http://sta.uwi.edu/rdifund/projects/agrinett/img/agriLogo2.png"


def notify(message_body,crop):
	result = Firebase.get("/users/"+crop,None)
	for sub in result:	
		registration_id =  sub 
		result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body,message_icon=message_icon)

	



if __name__ == "__main__":
	# result =Firebase.put("/users/carrot","Subscription",registration_id)
	result = Firebase.get("/users/carrot",None)
	for sub in result:	
		registration_id =  sub 
		result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body,message_icon=message_icon)

		

	# result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)

	
# # # Send to multiple devices by passing a list of ids.
# # registration_ids = ["<device registration_id 1>", "<device registration_id 2>", ...]
# # message_title = "Uber update"
# # message_body = "Hope you're having fun this weekend, don't forget to check today's news"
# print result