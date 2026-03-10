from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

TOKEN = "8625870692:AAHt96-dJquhz3MMoRIH02DdpNvV4pDvMuY"

db = sqlite3.connect("wallet.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS games (name TEXT, price INTEGER, key TEXT)")
db.commit()

menu = ReplyKeyboardMarkup([["💰 Portfel","🎮 Gry"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id,balance) VALUES (?,0)",(user_id,))
    db.commit()
    await update.message.reply_text("Bot sprzedaży gier", reply_markup=menu)

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE id=?",(user_id,))
    balance = cursor.fetchone()[0]
    await update.message.reply_text(f"Saldo: {balance} zł\n\nDoładowanie napisz: /add 50")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = int(context.args[0])
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?",(amount,user_id))
    db.commit()
    await update.message.reply_text("Saldo doładowane")

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT name,price FROM games")
    games = cursor.fetchall()
    text="Lista gier:\n"
    for g in games:
        text+=f"{g[0]} - {g[1]} zł\nKup: /buy {g[0]}\n\n"
    await update.message.reply_text(text)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = context.args[0]

    cursor.execute("SELECT price,key FROM games WHERE name=?",(name,))
    game = cursor.fetchone()

    cursor.execute("SELECT balance FROM users WHERE id=?",(user_id,))
    balance = cursor.fetchone()[0]

    if balance >= game[0]:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE id=?",(game[0],user_id))
        db.commit()
        await update.message.reply_text(f"Kupiono!\nKlucz: {game[1]}")
    else:
        await update.message.reply_text("Za mało środków")

app = ApplicationBuilder().token(8625870692:AAHt96-dJquhz3MMoRIH02DdpNvV4pDvMuY).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("wallet", wallet))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("games", games))
app.add_handler(CommandHandler("buy", buy))

app.run_polling()
