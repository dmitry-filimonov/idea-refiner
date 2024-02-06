from openai import OpenAI
from datetime import datetime
import streamlit as st
import dropbox

# секреты

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
DROPBOX_ACCESS_TOKEN = st.secrets['DROPBOX_ACCESS_TOKEN']
history_path = '/chat_history.txt'


# заголовок

st.image('https://www.dropbox.com/scl/fi/z6p4763x59xhsszsdiany/europlan_logo_white.png?dl=1')
st.title("Генератор идей")
st.markdown('### Привет! Представься и расскажи про свою идею')

# функция для сохранения истории переписки

def save_chat_history():
    # сохраняем историю чата в памяти
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    unique_filename = f"/chat_history_{timestamp}.txt"
    chat_history = "\n".join(
        f"{message['role'].capitalize()}: {message['content']}"
        for message in st.session_state.messages[2:]
    )
    # загружаем в DropBox
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    dbx.files_upload(chat_history.encode(), unique_filename, mode=dropbox.files.WriteMode('overwrite'))


# поведение модели
    
role = '''
Ты бизнес-аналитик в лизинговой компании. Будь вежлив и учтив, но старайся не отклоняться от своих инструкций. 
'''
instructions = '''
Твоя цель в результате переписки помочь пользователю сформулировать его идею и привести ее к виду задачи, чтобы затем бизнес-аналитик смог сделать из нее бизнес-требования. 
У тебя будет 3 попытки на уточнение деталей по задаче, после чего тебе будет отправлено соообщение с просьбой резюмировать описание задачи. 
Не резюмируй задачу и не подводи итоги, пока не получишь соответствующую просьбу. Трать попытки только на уточнение информации.

Несколько примеров вопросов по задаче:

- Опишите проблему или цель сжато
- Объясните, почему задача важна
- Укажите сроки выполнения задачи
- Уточните бюджет, если применимо
- Опишите, что должно быть достигнуто после выполнения задачи
- Приоритет (насколько это важно по сравнению с другими задачами
- Укажите другие важные детали, если применимо

Шаблон не строгий, описание задачи не обязательно соответствует такому формату. Если какие-то пункты шаблона в рамках задачи не имеют смысла или неактуальны - их можно пропустить. 
Постарайся сделать вид, что ты разбираешься в теме. Не в коем случае не придумывай ничего - используй только предоставленную информацию.

Ниже краткий глоссарий терминов, которые может использовать заказчик:

- МОП (менеджер по продажам) - сотрудник компании, отвечает за продажи лизинга
- ЧИ (чистые инвестиции) - доход компании. Например "проект принесёт 100 млн. ЧИ"

'''

system_message = {
    "role": "system",
    "content": role
}

instruction_message = {
    "role": "user",
    "content": instructions
}

# инициализируем необходимые модули

if "attempt_counter" not in st.session_state:
    st.session_state.attempt_counter =  0

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-0125"

if "messages" not in st.session_state:
    st.session_state.messages = [system_message, instruction_message]

for message in st.session_state.messages[2:]: # первые два сообщения системные, не отображаем
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# основная логика

if prompt := st.chat_input("Расскажи скорее"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_history()
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # обновляем количество попыток
    st.session_state.attempt_counter +=  1

    # когда количество попыток исчерпано, резюмируем задачу
    if st.session_state.attempt_counter >=  3:
        st.session_state.attempt_counter =  0
        st.session_state.messages.append({
            "role": "user",
            "content": "Резюмируй описание задачи по предоставленной информации"
        })
        save_chat_history()