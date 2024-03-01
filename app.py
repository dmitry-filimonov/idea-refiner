from openai import OpenAI
from datetime import datetime
import streamlit as st
import dropbox
from dropbox_auth import refresh_access_token

# секреты

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
refresh_token = st.secrets["REFRESH_TOKEN"]

# авторизация dropbox

try:
    tokens = refresh_access_token(refresh_token)
    access_token = tokens['access_token']
except Exception as e:
    print(e)

# заголовок

# st.image('https://www.dropbox.com/scl/fi/z6p4763x59xhsszsdiany/europlan_logo_white.png?dl=1') # ЧБ
# st.image('https://www.dropbox.com/scl/fi/cg05ald042d0g299cfi6a/europlan_logo-RGB.png?dl=1') # цветной
st.title("ИИ-ассистент БИП")
st.markdown('''
            ### Привет!
            Я помогу тебе оформить твою идею в таком виде,
            который поможет команде БИП максимально быстро ее реализовать. 
            Отвечай на уточняющие вопросы,
            но если они покажутся тебе бессмысленными - просто игнорируй их! 
            Не скупись на слова - чем больше ты напишешь контекста, 
            тем эффективнее ассистент сможет помочь тебе.
            ''')

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
    dbx = dropbox.Dropbox(access_token)
    dbx.files_upload(chat_history.encode(), unique_filename, mode=dropbox.files.WriteMode('overwrite'))


# поведение модели
    
role = '''
Ты бизнес-аналитик в лизинговой компании, отвечающий за продукт под названием "БИП" (Банк идей и предложений). Будь вежлив и учтив, но старайся не отклоняться от своих инструкций. 
'''
instructions = '''
Твоя цель в результате переписки помочь пользователю сформулировать его идею и привести ее к шаблону, чтобы затем эта идея могла быть реализована. Реузльтат твоей работы - текст идеи, не нужно предлагать
пользователю сделать презентацию или назначать встречи.

Перечень вопросов по идее:

1. Опишите ситуации, в которых можно применить ваше предложение 
 
2. Что и сколько сейчас теряет компания или потенциально приобретет в результате внедрения вашего предложения (денег, минут сотрудника, лояльности клиента и т.д.) в период (месяц, год и тд). На этом этапе можно собрать информацию от коллег, смежных подразделений 

3. Что вы предлагаете сделать? (здесь можно поэтапно описать реализацию так, как вы ее видите; приложить скриншоты; привести примеры существующей услуги у конкурентов )* 
 
4. Экономический эффект от внедрения вашего предложения?

Вопросы 1 и 2 обязательны, вопросы 3 и 4 опицональны. Формулировки вопросов не строгие, можно их уточнять другими словами, сохраняя суть. Если какие-то пункты шаблона в рамках задачи не имеют смысла или неактуальны - их можно пропустить. 
Постарайся сделать вид, что ты разбираешься в теме. Не в коем случае не придумывай ничего - используй только предоставленную информацию. Вопросы задавай по одному. После нескольких попыток тебе будет направлена просьба резюмировать задачу, постарайся разбить полученную информацию на пункты.

Ниже краткий глоссарий терминов, которые может использовать заказчик:

- МОП (менеджер по продажам) - сотрудник компании, отвечает за продажи лизинга
- ЧИ (чистые инвестиции) - доход компании. Например "проект принесёт 100 млн. ЧИ"
- САФО (система автоматизации фронт-офиса) - система для работы с контрагентами.
- ЦУЗ (центр управления задачами) - корпоративный таск-менеджер

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
    # save_chat_history()
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
        # st.session_state.messages.append({
        #     "role": "user",
        #     "content": "Резюмируй описание задачи по предоставленной информации"
        # })
        save_chat_history()