import httpx
import datetime
import json
import logging
from typing import NoReturn

import telegram
from telegram.error import NetworkError, Unauthorized
import db
from time import sleep

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

def generic(green_bot):

	green_bot.message.reply_text("Menu:")
	green_bot.message.reply_text("send 'pin 110011' to get vaccine availability at your pincode")
	green_bot.message.reply_text("send 'sub 110011' to subscribe for alerts when vaccine slots are available")
	green_bot.message.reply_text("send 'unsub 110011' to unsubscribe to alerts")
	green_bot.message.reply_text("send 'getsub' to get all your subscriptions")
	green_bot.message.reply_text("send 'update' to get updates for all your subs")
	green_bot.message.reply_text("For any problems, contact https://twitter.com/sslamba10")

def bg_process(d: db.DB, bot:telegram.Bot):
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
							bot.send_message(x, text="Alert! Capacity now available at {}".format(json.dumps(yy, indent=2)))


# Enable logging
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

d = db.DB()
# Define a few command handlers. These usually take the two arguments update and
# context.

def echo(bot: telegram.Bot) -> None:
	"""Echo the message the user sent."""
	global UPDATE_ID
	# Request updates after the last update_id
	for update in bot.get_updates(offset=UPDATE_ID, timeout=10):
		UPDATE_ID = update.update_id + 1

		if update.message:  # your bot can receive updates without messages
			if update.message.text:  # not all messages contain text
				# Reply to the message
				now=datetime.datetime.now()
				today = now.day
				hour = now.hour

				user_id=update.effective_user.id
				last_chat_text = update.message.text
				greetings = ('hello', 'hi', 'greetings', 'sup', '/start')
				split = last_chat_text.lower().split(" ")
				if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
					update.message.reply_text('Good Morning  {}'.format(update.effective_user.name))
					generic(green_bot=update)
					today += 1

				elif last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
					update.message.reply_text('Good Afternoon  {}'.format(update.effective_user.name))
					generic(green_bot=update)
					today += 1

				elif last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
					update.message.reply_text('Good Evening  {}'.format(update.effective_user.name))
					generic(green_bot=update)
					today += 1
				elif last_chat_text.lower() in greetings:
					update.message.reply_text('Good Day  {}'.format(update.effective_user.name))
					generic(green_bot=update)
					today += 1
				elif split:
					if split[0] == "pin":
						msg = rr(split[1])
						print(msg)
						if msg == []:
							msg.append("No sessions available")
						update.message.reply_text(json.dumps(msg, indent=2))
					elif split[0] == "sub":

						if len(split[1]) == 6:
							try:
								int(split[1])
								d.insert_sub("User",split[1],user_id)
								d.insert_usub("User",user_id,split[1])
								update.message.reply_text("Subscribed to {}".format(split[1]))
							except ValueError as e:
								print(repr(e))
								update.message.reply_text("Please enter a valid pincode, for example 'sub 123123'")
						else:
							update.message.reply_text("Please enter a valid pincode, for example 'sub 123123'")
					elif split[0] == "unsub":
						if len(split[1]) == 6:
							try:
								int(split[1])
								d.remove_sub("User",split[1],user_id)
								d.remove_usub("User",user_id,split[1])
								update.message.reply_text("Unsubscribed to {}".format(split[1]))
							except ValueError as e:
								print(repr(e))
								update.message.reply_text("Please enter a valid pincode, for example 'unsub 123123'")
						else:
							update.message.reply_text("Please enter a valid pincode, for example 'unsub 123123'")

					elif split[0] == "getsub":
						msg=d.get_all_usub("User",user_id)
						if msg is not None:
							update.message.reply_text("Subscribed to {}".format(json.dumps(json.loads(msg["value"]), indent=2)))
						else:
							update.message.reply_text("No subscriptions available")
					elif split[0] == "update":
						m=d.get_all_usub("User",user_id)
						if m is None:
							update.message.reply_text("No subscriptions")
						else:
							for x in json.loads(m["value"]):
								msg = rr(x)
								print(msg)
								if msg == []:
									msg.append("No sessions available")
								update.message.reply_text(json.dumps(msg, indent=2))



UPDATE_ID = None


def main() -> NoReturn:
	"""Run the bot."""
	global UPDATE_ID
	# Telegram Bot Authorization Token
	bot = telegram.Bot('TOKEN')

	# get the first pending update_id, this is so we can skip over it in case
	# we get an "Unauthorized" exception.
	try:
		UPDATE_ID = bot.get_updates()[0].update_id
	except IndexError:
		UPDATE_ID = None

	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	while True:
		try:
			echo(bot)
			bg_process(d,bot)
			sleep(5)
		except NetworkError:
			sleep(1)
		except Unauthorized:
			# The user has removed or blocked the bot.
			UPDATE_ID += 1
if __name__ == '__main__':
	main()