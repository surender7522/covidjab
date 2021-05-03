import httpx
import os
from time import sleep
import datetime
import requests
import json

def rr(pincode):
	headers = {'Accept-Language': 'hi_IN', 'accept': 'application/json'}
	now = datetime.datetime.now()
	r = httpx.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}-{}-{}'.format(pincode,now.day,now.month,now.year),headers=headers)
	print(r.json())
	jsond=r.json()
	ret_list=[]
	for i in (jsond["centers"]):
		ret_list.append({"name": i["name"], "available_capacity": i["sessions"][0]["available_capacity"], "min age limit": i["sessions"][0]["min_age_limit"],
						"vaccine": i["sessions"][0]["vaccine"], "date": i["sessions"][0]["date"]})
	return ret_list

def generic(green_bot,last_chat_id):
	greet_bot.send_message(last_chat_id, "Menu:")
	greet_bot.send_message(last_chat_id, "send 'pin 110011' to get vaccine availability at your pincode")
	green_bot.send_message(last_chat_id, "Adding more features soon, like subscriptions, stay tuned.")

class BotHandler:

	def __init__(self, token):
		self.token = token
		self.api_url = "https://api.telegram.org/bot{}/".format(token)

	def get_updates(self, offset=None, timeout=30):
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
greetings = ('hello', 'hi', 'greetings', 'sup')
now = datetime.datetime.now()


def main():
	new_offset = None
	today = now.day
	hour = now.hour

	while True:
		greet_bot.get_updates(new_offset)

		last_update = greet_bot.get_last_update()
		if last_update == {}:
			sleep(10)
			continue
		print(last_update)

		last_update_id = last_update['update_id']
		last_chat_text = last_update['message']['text']
		last_chat_id = last_update['message']['chat']['id']
		last_chat_name = last_update['message']['chat']['first_name']
		print(last_update_id)
		print(last_chat_text)
		print(last_chat_id)
		print(last_chat_name)
		print(today)
		print(hour)
		split = last_chat_text.split(" ")
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
				greet_bot.send_message(last_chat_id, json.dumps(msg, indent=2))

		new_offset = last_update_id + 1

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		exit()