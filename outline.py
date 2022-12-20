from telegram.ext import Updater, Dispatcher, JobQueue
import datetime

# Set up the Updater and Dispatcher
updater = Updater(token='YOUR_API_TOKEN', use_context=True)
dispatcher = updater.dispatcher

# Set up the JobQueue
job_queue = JobQueue()

# Define a function that will be called by the job
def check_for_report(context):
    # Get the current time
    now = datetime.datetime.now()

    # Check if it's time for the report
    if now.hour == 18 and now.minute == 0:
        # Send a warning message to users who have not sent their report
        context.bot.send_message(chat_id='YOUR_CHAT_ID', text='Please send your report by 6pm!')

        # Kick users who have not sent their report
        context.bot.kick_chat_member(chat_id='YOUR_CHAT_ID', user_id='USER_ID')

# Schedule the job to run every minute
job_queue.run_repeating(check_for_report, interval=60, first=0)

# Start the bot
updater.start_polling()
