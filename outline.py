import datetime
import mysql.connector
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, JobQueue

# Connect to the database
cnx = mysql.connector.connect(user='USERNAME', password='PASSWORD', host='HOST', database='DATABASE')

# Set up the Updater and Dispatcher
updater = Updater(token='YOUR_API_TOKEN', use_context=True)
dispatcher = updater.dispatcher

# Set up the JobQueue
job_queue = JobQueue()

# Define a function that will be called by the job
def send_reminder(context):
    # Get the current time
    now = datetime.datetime.now()

    # Check if it's time to send the reminder
    cursor = cnx.cursor()
    cursor.execute('SELECT reminder_hour, reminder_minute FROM reminders WHERE user_id=%s', (context.user_data['user_id'],))
    row = cursor.fetchone()
    if now.hour == row[0] and now.minute == row[1]:
        # Send a reminder message to the user
        context.bot.send_message(chat_id=context.user_data['user_id'], text='Please remember to send your report with a photo and text (optional) by your deadline!')

# Define a function that will be called when the /setreminder command is received
def set_reminder(update, context):
    # Split the input into separate
    time_parts = update.message.text.split()[1].split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1])

    # Store the reminder time in the database
    cursor = cnx.cursor()
    cursor.execute('INSERT INTO reminders (user_id, reminder_hour, reminder_minute, `group`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE reminder_hour=%s, reminder_minute=%s, `group`=%s', (update.effective_user.id, hour, minute, update.effective_chat.title, hour, minute, update.effective_chat.title))
    cnx.commit()

# Define a function that will be called when the /setdeadline command is received
def set_deadline(update, context):
    # Split the input into separate time and date parts
    time_parts = update.message.text.split()[1].split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1])

    # Store the deadline time in the database
    cursor = cnx.cursor()
    cursor.execute('INSERT INTO reminders (user_id, deadline_hour, deadline_minute, `group`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE deadline_hour=%s, deadline_minute=%s, `group`=%s', (update.effective_user.id, hour, minute, update.effective_chat.title, hour, minute, update.effective_chat.title))
    cnx.commit()

# Define a function that will be called when a message is received
def message_received(update, context):
    # Get the current time
    now = datetime.datetime.now()

    # Check if the message was sent after the deadline
    cursor = cnx.cursor()
    cursor.execute('SELECT deadline_hour, deadline_minute FROM reminders WHERE user_id=%s', (update.effective_user.id,))
    row = cursor.fetchone()
    if now.hour > row[0] or (now.hour == row[0] and now.minute >= row[1]):
        # Send a message to the user indicating that they missed the deadline
        context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, you missed the deadline for sending your report.')
    else:
        # Send a message to the user indicating that their report has been received
        context.bot.send_message(chat_id=update.effective_chat.id, text='Thank you for sending your report!')

# Add the CommandHandler and MessageHandler objects to the Dispatcher
dispatcher.add_handler(CommandHandler('setreminder', set_reminder))
dispatcher.add_handler(CommandHandler('setdeadline', set_deadline))
dispatcher.add_handler(MessageHandler(filters=None, callback=message_received))

# Start the bot
updater.start_polling()
