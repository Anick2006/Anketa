from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove

TOKEN = '6846510496:AAFvqymD3NNDsQlmEVL5JDbgxVpDeQueB14'
credentials_file = 'credentials.json'
spreadsheet_id = '1-Zvg8i7Yx75dUSROeuiZd_YH4vpY3XvQQq37dY7_7C8'


RUSSIAN_QUESTIONS = [
    "1.Ваша фамилия по загран паспорту",
    "2. Ваше имя по загран паспорту",
    "3. Дата рождения дд мм гггг",
    "4. Место рождения по загран паспорту",
    "5. Серия и номер загран паспорта?",
    "6. Дата выдачи загран паспорта? дд мм гггг",
    "7. Срок истечения загран паспорта?",
    "8. Место жительства:",
    "9. Семейное положение: \n(•Женат)\n(•Замужем) \n(•холост) \n(•разведен/а) \n(•вдовец/вдова)",
    "10. Дети\n(•ДА)\n(•НЕТ)",
    "11. Образование:\n(• Среднее школа)\n(• Средне-специальное)\n(• Бакалавр)\n(• Магистр)\n(• Доктор наук)",
    "12. Название учебного заведения",
    "13. Были ли за границей за последние 5 лет?\n(•ДА)\n(•НЕТ)",
    "14. Имеется ли у вас имущество \n Например:Автомашина, дом, дача и т.д?\n(•ДА)\n(•НЕТ)",
    "15. В настоящее время работаете?\n(•ДА)\n(•НЕТ)",
    "16. Место работы и должность:",
    "17. Вы раньше подавали заявление на получение Канадской визы?\n(•ДА)\n(•НЕТ)"
]

UZBEK_CYRILLIC_QUESTIONS = [
    "1. Фамилиянгиз загран паспорт бўйича",
    "2. Исмингиз загран паспорт буйича",
    "3. Туғилган санангиз кк оо йййй",
    "4. Туғилган жойингиз загран паспорт бўйича",
    "5. Загран паспорт серияси ва рақами",
    "6. Загран паспорт берилган сана кк оо йййй",
    "7. Загран паспортнинг амал қилиш муддати тугайдиган сана кк оо йййй",
    "8. Яшаш манзилингиз: ",
    "9. Оилавий холатингиз:\n(•Оилали)\n(•Турмуш қурмаган)\n(•Ажрашган)\n(•Бева)",
    "10. Фарзандингиз борми\n(Xа)\n(Йўқ)",
    "11. Маълумотингиз:\n(•Ўрта мактаб)\n(•Ўрта-махсус)\n(•Бакалавр)\n(•Магистр)\n(•Фан доктори)",
    "12. Тамомлаган ўқув юртигиз номи",
    "13. Сўнгги 5 йил мобайнида хорижга чиққанмисиз \n(•Xа)\n(•Йўқ)",
    "14. Номингизда мулк борми - Автомашина, уй, дала ховли ва бошқалар\n(•Xа)\n(•Йўқ)",
    "15. Ҳозирда ишлайсизми \n(•Xа)\n(•Йўқ)",
    "16. Иш жойингиз ва лавозимингиз: ",
    "17. Илгари Канада давлати визасини олиш учун хужжат топширганмисиз\n(•Xа)\n(•Йўқ)"
]

UZBEK_LATIN_QUESTIONS = [
    "1.Familiyangiz zagran pasport bo'yicha",
    "2. Ismingiz zagran pasport bo'yicha",
    "3. Tug'ilgan sanangiz dd mm yyyy",
    "4. Tug'ilgan joyingiz zagran pasport bo'yicha",
    "5. Zagran pasport seriyasi va raqami ",
    "6. Zagran pasport berilgan sanadd mm yyyy",
    "7. Zagran passportning amal qilish muddati tugaydigan sana dd mm yyyy",
    "8. Yashash manzilingiz: ",
    "9. Oilaviy holatingiz:\n(•Oilali)\n(•Turmush qurmagan)\n(•Ajrashgan)\n(•Beva)",
    "10. Farzandingiz bormi\n(•Ha)\n(•Yo'q)",
    "11. Ma'lumotingiz:\n(•O'rta maktab)\n(•O'rta maxsus)\n(•Bakalavr)\n(•Magistr)\n(•Fan doktori)",
    "12. Tamomlagan o/'quv yurtingiz nomi",
    "13. So'nggi 5 yil mobaynida horijga chiqqanmisiz\n(•Ha)\n(•Yo'q)",
    "14. Nomingizda mulk bormi avtomashina, uy, dala hovli va boshqalar\n(•Ha)\n(•Yo'q) ",
    "15. Hozirda ishlaysizmi\n(•Ha)\n(•Yo'q)",
    "16. Ish joyingiz va lavozimingiz: ",
    "17. Ilgari Kanada davlati vizasini olish uchun hujjat topshirganmisiz\n(•Ha)\n(•Yo'q)"
]

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(spreadsheet_id)
sheet = spreadsheet.get_worksheet(0)  # 0 refers to the first sheet

def is_numeric(s: str) -> bool:
    return s.replace(' ', '').isdigit()

def has_options(question: str) -> bool:
    return "(" in question and ")" in question

def is_valid_date_format(s: str) -> bool:
    pattern = r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$"
    return re.match(pattern, s) is not None

def send_question(update, context, user_id, question):
    if has_options(question):
        options = re.findall(r'\((.*?)\)', question)
        keyboard = [[KeyboardButton(option.strip())] for option in options]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text=question.split("(")[0], reply_markup=reply_markup)
    else:
        reply_markup = ReplyKeyboardRemove()  # Удаление текущей клавиатуры
        context.bot.send_message(chat_id=update.effective_chat.id, text=question, reply_markup=reply_markup)


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("Узбек тили(кирилча)")],
        [KeyboardButton("O'zbek tili (lotincha)")],
        [KeyboardButton("Русский язык")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
    update.message.reply_text('👋Приветствую! \nВыберите язык для продолжения:\n\n👋Assalomu aleykum! \n Davom ettirish tilni tanlang: ', reply_markup=reply_markup)

def handle_language_choice(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    text = update.message.text
    
    if text == "Узбек тили(кирилча)":
        context.user_data[user_id] = {"index": 0, "questions": UZBEK_CYRILLIC_QUESTIONS, "answers": [], "language": "uzb"}
    elif text == "O'zbek tili (lotincha)":
        context.user_data[user_id] = {"index": 0, "questions": UZBEK_LATIN_QUESTIONS, "answers": [], "language": "uzb"}
    elif text == "Русский язык":
        context.user_data[user_id] = {"index": 0, "questions": RUSSIAN_QUESTIONS, "answers": [], "language": "rus"}
    else:
        update.message.reply_text("Пожалуйста, выберите язык из предложенных вариантов.")
        return
    
    send_question(update, context, user_id, context.user_data[user_id]["questions"][0])


def message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = context.user_data.get(user_id, {})
    
    if "questions" not in user_data or "index" not in user_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, начните с выбора языка, используя команду /start.")
        return

    current_question = user_data["questions"][user_data["index"]]

    if user_data["index"] in [2, 5, 6] and not is_valid_date_format(update.message.text):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ответ на этот вопрос должен быть цифрами и в формате dd.mm.yyyy. Пожалуйста, введите снова.")
        return
    if has_options(current_question):
        if update.message.text in [option.strip() for option in re.findall(r'\((.*?)\)', current_question)]:
            user_data.setdefault("answers", []).append(update.message.text)  # Сохраняем только ответ
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, выберите один из предложенных вариантов ответа.")
            return
    else:
        user_data.setdefault("answers", []).append(update.message.text)  # Сохраняем только ответ

    if user_data["index"] >= len(user_data["questions"]) - 1:
        user_data["answers"].insert(0, user_data["language"])  # Вставляем язык вместо ID пользователя
        sheet.append_row(user_data["answers"])
        del context.user_data[user_id]
        update.message.reply_text("Благодарю за информацию, с вами свяжутся в ближайшее время!")
    else:
        user_data["index"] += 1
        send_question(update, context, user_id, user_data["questions"][user_data["index"]])

    context.user_data[user_id] = user_data



def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(Узбек тили\(кирилча\)|O\'zbek tili \(lotincha\)|Русский язык)$'), handle_language_choice))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()