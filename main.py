import httpx
import os
from time import sleep
import datetime
import requests
import json
import db

def rr(pincode):
	headers = {'Accept-Language': 'hi_IN', 'accept': 'application/json'}
	now = datetime.datetime.now()
	r = httpx.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}-{}-{}'.format(pincode,now.day,now.month,now.year),headers=headers)
	print(r.json())
	jsond=r.json()
	ret_list=[]
	for i in (jsond["centers"]):
		for j in i["sessions"]:
			ret_list.append({"name": i["name"], "available_capacity": j["available_capacity"], "min age limit": j["min_age_limit"],
							"vaccine": j["vaccine"], "date": j["date"]})
	return ret_list

def generic(green_bot,last_chat_id):
	greet_bot.send_message(last_chat_id, "Menu:")
	greet_bot.send_message(last_chat_id, "send 'pin 110011' to get vaccine availability at your pincode")
	greet_bot.send_message(last_chat_id, "send 'sub 110011' to subscribe for alerts when vaccine slots are available")
	greet_bot.send_message(last_chat_id, "send 'unsub 110011' to unsubscribe to alerts")
	greet_bot.send_message(last_chat_id, "send 'getsub' to get all your subscriptions")
	greet_bot.send_message(last_chat_id, "send 'update' to get updates for all your subs")
	green_bot.send_message(last_chat_id, "For any problems, contact https://twitter.com/sslamba10")

class BotHandler:

	def __init__(self, token):
		self.token = token
		self.api_url = "https://api.telegram.org/bot{}/".format(token)

	def get_updates(self, offset=None, timeout=10):
		method = 'getUpdates'
		params = {'timeout': timeout, 'offset': offset}
		resp = requests.get(self.api_url + method, params)
		result_json = resp.json()['result']
		return result_json

	def send_message(self, chat_id, text):
		params = {'chat_id': chat_id, 'text': text}
		method = 'sendMessage'
		resp = requests.post(self.api_url + method, params)
		return resp

	def get_last_update(self):
		get_result = self.get_updates()

		if len(get_result) > 0:
			last_update = get_result[-1]
		else:
			return {}

		return last_update

greet_bot = BotHandler(str(os.getenv("token","")))
greetings = ('hello', 'hi', 'greetings', 'sup', '/start')
now = datetime.datetime.now()

def bg_process(d):
	m=d.get_all_sub("User")
	for a in m:
		if a["value"] != "[]" and len(str(a["key"]))==6:
			msg = rr(a["key"])
			print(msg)
			if msg == []:
				msg.append("No sessions available")
			else:
				for yy in msg:
					if yy["available_capacity"] > 0:
						for x in json.loads(a["value"]):
							print(x)
							greet_bot.send_message(x, "Alert! Capacity now available at {}".format(json.dumps(yy, indent=2)))

def main():
	new_offset = None
	today = now.day
	hour = now.hour
	d = db.DB()

	while True:
		greet_bot.get_updates(new_offset)

		last_update = greet_bot.get_last_update()
		if last_update == {}:
			#update all
			bg_process(d)
			continue
		print(last_update)
		if "message" not in last_update.keys():
			continue
		last_update_id = last_update['update_id']
		last_chat_text = last_update['message']['text']
		last_chat_id = last_update['message']['chat']['id']
		last_chat_name = last_update['message']['chat']['first_name']
		user_id = last_update["message"]["from"]["id"]
		print(last_update_id)
		print(last_chat_text)
		print(last_chat_id)
		print(last_chat_name)
		print(today)
		print(hour)
		split = last_chat_text.lower().split(" ")
		if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
			greet_bot.send_message(last_chat_id, 'Good Morning  {}'.format(last_chat_name))
			generic(green_bot=greet_bot,last_chat_id=last_chat_id)
			today += 1

		elif last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
			greet_bot.send_message(last_chat_id, 'Good Afternoon {}'.format(last_chat_name))
			generic(green_bot=greet_bot,last_chat_id=last_chat_id)
			today += 1

		elif last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
			greet_bot.send_message(last_chat_id, 'Good Evening  {}'.format(last_chat_name))
			generic(green_bot=greet_bot,last_chat_id=last_chat_id)
			today += 1
		elif last_chat_text.lower() in greetings:
			greet_bot.send_message(last_chat_id, 'Good day  {}'.format(last_chat_name))
			generic(green_bot=greet_bot,last_chat_id=last_chat_id)
			today += 1
		elif split:
			if split[0] == "pin":
				msg = rr(split[1])
				print(msg)
				if msg == []:
					msg.append("No sessions available")
				greet_bot.send_message(user_id, json.dumps(msg, indent=2))
			elif split[0] == "sub":

				if len(split[1]) == 6:
					try:
						int(split[1])
						d.insert_sub("User",split[1],user_id)
						d.insert_usub("User",user_id,split[1])
						greet_bot.send_message(user_id, "Subscribed to {}".format(split[1]))
					except ValueError as e:
						print(repr(e))
						greet_bot.send_message(user_id, "Please enter a valid pincode, for example 'sub 123123'")
				else:
					greet_bot.send_message(user_id, "Please enter a valid pincode, for example 'sub 123123'")
			elif split[0] == "unsub":
				if len(split[1]) == 6:
					try:
						int(split[1])
						d.remove_sub("User",split[1],user_id)
						d.remove_usub("User",user_id,split[1])
						greet_bot.send_message(user_id, "Unsubscribed to {}".format(split[1]))
					except ValueError as e:
						print(repr(e))
						greet_bot.send_message(user_id, "Please enter a valid pincode, for example 'unsub 123123'")
				else:
					greet_bot.send_message(user_id, "Please enter a valid pincode, for example 'unsub 123123'")

			elif split[0] == "getsub":
				msg=d.get_all_usub("User",user_id)
				if msg is not None:
					greet_bot.send_message(user_id, "Subscribed to {}".format(json.dumps(json.loads(msg["value"]), indent=2)))
				else:
					greet_bot.send_message(user_id, "No subscriptions available")
			elif split[0] == "update":
				m=d.get_all_usub("User",user_id)
				for x in json.loads(m["value"]):
					msg = rr(x)
					print(msg)
					if msg == []:
						msg.append("No sessions available")
					greet_bot.send_message(user_id, json.dumps(msg, indent=2))
		new_offset = last_update_id + 1
		bg_process(d)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		exit()