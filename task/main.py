import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Вопросы и ответы
QUIZ_DATA = [
    {
        'question': 'В каком веке появилось название "Басманная слобода"?',
        'options': ['XIV век', 'XV век', 'XVI век', 'XVII век'],
        'correct': 3,
        'explanation': 'Басманная слобода появилась в XVII веке, здесь жили мастера, делавшие "басманы" - металлические украшения для книг и икон.'
    },
    {
        'question': 'Какое знаменитое учебное заведение находится в Басманном районе?',
        'options': ['МГУ', 'МГТУ им. Баумана', 'МГИМО', 'РЭУ им. Плеханова'],
        'correct': 1,
        'explanation': 'МГТУ им. Баумана - один из старейших и престижнейших технических вузов России, основанный в 1830 году.'
    },
    {
        'question': 'Какой храм является старейшим в Басманном районе?',
        'options': ['Храм Никиты Мученика', 'Елоховский собор', 'Храм Космы и Дамиана', 'Храм Вознесения Господня'],
        'correct': 0,
        'explanation': 'Храм Никиты Мученика на Старой Басманной построен в 1517 году и является старейшим в районе.'
    },
    {
        'question': 'Какое историческое событие связано с Басманным районом в 1812 году?',
        'options': ['Коронование Александра I', 'Пожар Москвы', 'Бородинская битва', 'Подписание мирного договора'],
        'correct': 1,
        'explanation': 'Во время пожара Москвы в 1812 году Басманный район сильно пострадал, многие здания сгорели.'
    },
    {
        'question': 'Какой известный русский поэт жил на Старой Басманной улице?',
        'options': ['Александр Пушкин', 'Михаил Лермонтов', 'Сергей Есенин', 'Владимир Маяковский'],
        'correct': 0,
        'explanation': 'Александр Пушкин жил в доме №36 на Старой Басманной у своего дяди Василия Львовича Пушкина.'
    },
    {
        'question': 'Какое необычное прозвище получила Басманная больница в народе?',
        'options': ['"Каменная"', '"Красная"', '"Желтая"', '"Белая"'],
        'correct': 2,
        'explanation': 'Басманная больница получила прозвище "Желтая" из-за цвета своих стен.'
    },
    {
        'question': 'Какой известный московский вокзал находится в Басманном районе?',
        'options': ['Казанский', 'Курский', 'Ярославский', 'Ленинградский'],
        'correct': 1,
        'explanation': 'Курский вокзал, построенный в 1896 году, расположен на границе Басманного района.'
    },
    {
        'question': 'Какое здание в Басманном районе называют "Дом-комод"?',
        'options': ['Дом Апраксиных', 'Дом Мусина-Пушкина', 'Дом Демидова', 'Дом Тутолмина'],
        'correct': 1,
        'explanation': 'Дом Мусина-Пушкина на Разгуляе (1750-е гг.) называют "Дом-комод" за его необычную архитектуру.'
    },
    {
        'question': 'Какой музей Басманного района посвящен истории района?',
        'options': ['Музей "Садовое кольцо"', 'Музей Москвы', 'Музей Басманного района', 'Музей "Старая Басманная"'],
        'correct': 0,
        'explanation': 'Музей "Садовое кольцо" на Проспекте Мира рассказывает об истории Басманного и других центральных районов Москвы.'
    },
    {
        'question': 'Какое современное прозвище получил Басманный район?',
        'options': ['"Силиконовая слобода"', '"Кремниевый холм"', '"IT-долина"', '"Московская Калифорния"'],
        'correct': 0,
        'explanation': 'Басманный район называют "Силиконовой слободой" из-за большого количества IT-компаний, расположенных здесь.'
    }
]

class QuizBot:
    def __init__(self):
        self.user_data = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        self.user_data[user_id] = {'score': 0, 'question_index': 0}

        keyboard = [
            [InlineKeyboardButton("Начать викторину 🚀", callback_data="start_quiz")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Добро пожаловать в викторину о Басманном районе!\n"
            "Проверьте свои знания и узнайте интересные факты.\n\n"
            "Нажмите кнопку ниже, чтобы начать:",
            reply_markup=reply_markup
        )

    async def handle_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        if query.data == "start_quiz":
            self.user_data[user_id] = {'score': 0, 'question_index': 0}
            await self.send_question(update, context)
        elif query.data == "restart_quiz":
            self.user_data[user_id] = {'score': 0, 'question_index': 0}
            await query.edit_message_text(text="Викторина начата заново!")
            await self.send_question(update, context)
        elif query.data == "continue":
            await self.send_question(update, context)
        else:
            await self.handle_answer(update, context)

    async def send_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        user_state = self.user_data.get(user_id, {'score': 0, 'question_index': 0})
        question_num = user_state['question_index']

        if question_num < len(QUIZ_DATA):
            question_data = QUIZ_DATA[question_num]
            keyboard = [
                [InlineKeyboardButton(option, callback_data=str(i))]
                for i, option in enumerate(question_data['options'])
            ]
            keyboard.append([InlineKeyboardButton("Начать заново 🔄", callback_data="restart_quiz")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            text = f'Вопрос {question_num + 1}/{len(QUIZ_DATA)}:\n{question_data["question"]}'

            if update.callback_query:
                await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
            else:
                await update.message.reply_text(text=text, reply_markup=reply_markup)
        else:
            await self.finish_quiz(update, context, user_id)

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        user_state = self.user_data.get(user_id, {'score': 0, 'question_index': 0})
        question_num = user_state['question_index']
        selected_option = int(query.data)

        question_data = QUIZ_DATA[question_num]
        is_correct = selected_option == question_data['correct']

        if is_correct:
            user_state['score'] += 1
            response_text = '✅ Верно!'
        else:
            correct_answer = question_data['options'][question_data['correct']]
            response_text = f'❌ Неверно! Правильный ответ: {correct_answer}\n\n{question_data["explanation"]}'

        # Увеличиваем счетчик вопросов
        user_state['question_index'] += 1

        keyboard = [
            [InlineKeyboardButton("Следующий вопрос ➡️", callback_data="continue")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f'{response_text}\n\nТекущий счёт: {user_state["score"]}/{len(QUIZ_DATA)}',
            reply_markup=reply_markup
        )

    async def finish_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
        final_score = self.user_data.get(user_id, {}).get('score', 0)

        keyboard = [
            [InlineKeyboardButton("Начать заново 🔄", callback_data="restart_quiz")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'🏆 Викторина завершена! Ваш результат: {final_score}/{len(QUIZ_DATA)}\n\n'
                 'Хотите попробовать ещё раз?',
            reply_markup=reply_markup
        )

        if user_id in self.user_data:
            del self.user_data[user_id]


def main():
    bot_token = "7967185943:AAFLxB9dkNzmnOrO8mKuq6Ik6Og69R8M8Is" 

    quiz_bot = QuizBot()

    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", quiz_bot.start))
    application.add_handler(CallbackQueryHandler(quiz_bot.handle_buttons))

    try:
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        if application.running:
            application.stop()


if __name__ == '__main__':
    main()
