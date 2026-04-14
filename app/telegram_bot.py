import os
import asyncio
from datetime import time
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, schemas
from datetime import date

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in .env file")

user_chat_ids = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_chat_ids.add(chat_id)
    await update.message.reply_text(
        "Welcome to TaskTracker! Use /habits to see your habits, /add <habit_name> to add a new habit, /checkin <habit_id> to log today."
    )

async def add_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /add <habit_name>")
        return
    name = " ".join(context.args)
    db = SessionLocal()
    try:
        habit = crud.create_habit(db, schemas.HabitCreate(name=name))
        await update.message.reply_text(f"Habit '{habit.name}' added with ID {habit.id}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    finally:
        db.close()

async def list_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    habits = crud.get_habits(db)
    if not habits:
        await update.message.reply_text("No habits yet. Add one with /add <name>")
    else:
        msg = "Your habits:\n"
        for h in habits:
            streak = crud.get_streak(db, h.id)
            msg += f"{h.id}: {h.name} (streak: {streak})\n"
        await update.message.reply_text(msg)
    db.close()

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /checkin <habit_id>")
        return
    try:
        habit_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Habit ID must be a number")
        return
    db = SessionLocal()
    habit = crud.get_habit(db, habit_id)
    if not habit or not habit.active:
        await update.message.reply_text("Habit not found")
        db.close()
        return
    crud.log_habit(db, habit_id, date.today(), True)
    streak = crud.get_streak(db, habit_id)
    await update.message.reply_text(f"✅ Checked in! Streak: {streak}")
    db.close()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("checkin_"):
        habit_id = int(data.split("_")[1])
        db = SessionLocal()
        crud.log_habit(db, habit_id, date.today(), True)
        streak = crud.get_streak(db, habit_id)
        await query.edit_message_text(f"✅ Checked in habit {habit_id}! Streak: {streak}")
        db.close()

async def daily_reminder_callback(context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    habits = crud.get_habits(db)
    for chat_id in user_chat_ids:
        keyboard = []
        for h in habits:
            keyboard.append([InlineKeyboardButton(h.name, callback_data=f"checkin_{h.id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Time to check in your habits for today!",
            reply_markup=reply_markup
        )
    db.close()

def run_bot():
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_habit))
    application.add_handler(CommandHandler("habits", list_habits))
    application.add_handler(CommandHandler("checkin", checkin))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Job queue
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(daily_reminder_callback, time=time(hour=20, minute=0))
    
    # Run the bot without signal handlers (pass empty list for stop_signals)
    application.run_polling(stop_signals=[])