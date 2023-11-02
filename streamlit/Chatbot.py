import streamlit as st
import boto3
import uuid

# Set the name of your Lex bot
bot_name = 'xxxxxxxx'
bot_alias_id = 'xxxxxxxx'
bot_region = 'xxxxxxx'

# Create the Lex client
lex = boto3.client('lexv2-runtime', region_name=bot_region)
session_attrs = {}

user_id = ''
USER_ICON = "images/user-icon.png"
AI_ICON = "images/ai-icon.png"
MAX_HISTORY_LENGTH = 5

if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if "chats" not in st.session_state:
    st.session_state.chats = [
        {
            'id': 0,
            'question': '',
            'answer': ''
        }
    ]

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""

st.set_page_config(page_title='Content Bot')
st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                    width: 100rem
                }
                .element-container img {
                    background-color: #000000;
                }

                .main-header {
                    font-size: 24px;
                }
        </style>
        """, unsafe_allow_html=True)


def write_logo():
    col1, col2, col3 = st.columns([5, 1, 5])
    with col2:
        st.image(AI_ICON, use_column_width='always')


def write_top_bar():
    col1, col2, col3 = st.columns([1, 10, 2])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        provider = "Meta Open-LLama-2-13B"
        header = f"Marketing Content Generator powered by Amazon Kendra and {provider}!"
        st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)
    with col3:
        clear = st.button("Clear Chat")
    return clear


clear = write_top_bar()

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []


def handle_input():
    input = st.session_state.input
    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)

    chat_history = st.session_state["chat_history"]
    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    # llm_chain = st.session_state['llm_chain']
    # chain = st.session_state['llm_app']

    response = lex.recognize_text(
        botId=bot_name,
        botAliasId=bot_alias_id,
        localeId='en_US',
        sessionId=user_id,
        text=input,
        sessionState=session_attrs)
    try:
        answer = response['messages'][0]['content']
    except:
        answer = 'Sorry, No information Available'
    result = {'answer', answer}
    chat_history.append((input, answer))

    # document_list = []
    # if 'source_documents' in result:
    #     for d in result['source_documents']:
    #         if not (d.metadata['source'] in document_list):
    #             document_list.append((d.metadata['source']))

    st.session_state.answers.append({
        'answer': answer,
        'id': len(st.session_state.questions)
    })
    st.session_state.input = ""


def write_user_message(md):
    col1, col2 = st.columns([1, 12])

    with col1:
        st.image(USER_ICON, use_column_width='always')
    with col2:
        st.warning(md['question'])


def render_result(result):
    answer, sources = st.tabs(['Answer', 'Sources'])
    with answer:
        render_answer(result['answer'])


def render_answer(answer):
    print(answer)
    col1, col2 = st.columns([1, 12])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        st.info(answer)


def render_sources(sources):
    col1, col2 = st.columns([1, 12])
    with col2:
        with st.expander("Sources"):
            for s in sources:
                st.write(s)


# Each answer will have context of the question asked in order to associate the provided feedback with the respective question
def write_chat_message(md, q):
    chat = st.container()
    with chat:
        render_answer(md['answer'])
        # render_sources(md['sources'])


with st.container():
    for (q, a) in zip(st.session_state.questions, st.session_state.answers):
        write_user_message(q)
        write_chat_message(a, q)

st.markdown('---')
input = st.text_input("You are talking to an AI, ask any question.", key="input", on_change=handle_input)
