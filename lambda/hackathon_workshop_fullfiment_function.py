from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#Assign the name of the AWS Lex Intent being used
lex_search_intent_name='APKnowledgeSearch'
#Assign the Kendra Index Name
kendra_index_id = '824b1cc9-07ce-43bd-89ba-a06a1987174e'

MAX_HISTORY_LENGTH = 5


def build_chain():
    # region = os.environ["AWS_REGION"]
    # credentials_profile_name = os.environ['AWS_PROFILE']

    # print(credentials_profile_name)

    llm = Bedrock(
        # credentials_profile_name=credentials_profile_name,
        # region_name=region,
        model_kwargs={"max_tokens_to_sample": 300, "temperature": 1, "top_k": 250, "top_p": 0.999,
                      "anthropic_version": "bedrock-2023-05-31"},
        model_id="anthropic.claude-v2"
    )

    retriever = AmazonKendraRetriever(index_id=kendra_index_id,
                                      top_k=5,
                                      # region_name=region
                                     )

    prompt_template = """Human: This is a friendly conversation between a human and an AI. 
  The AI is talkative and provides specific details from its context but limits it to 240 tokens.
  If the AI does not know the answer to a question, it truthfully says it 
  does not know.

  Assistant: OK, got it, I'll be a talkative truthful AI assistant.

  Human: Here are a few documents in <documents> tags:
  <documents>
  {context}
  </documents>
  Based on the above documents, provide a detailed answer for, {question} 
  Answer "don't know" if not present in the document. 

  Assistant:
  """
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    condense_qa_template = """{chat_history}
  Human:
  Given the previous conversation and a follow up question below, rephrase the follow up question
  to be a standalone question.

  Follow Up Question: {question}
  Standalone Question:

  Assistant:"""
    standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        condense_question_prompt=standalone_question_prompt,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": PROMPT},
        verbose=True)

    # qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, qa_prompt=PROMPT, return_source_documents=True)
    return qa


def run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})


def dispatch_intent(event):
    try:
        chat_history = []
        final_response = []
        qa = build_chain()
        logger.debug('event={}'.format(event))
        logger.debug('bot.asked.question={}'.format(event['inputTranscript']))
        if (len(chat_history) == MAX_HISTORY_LENGTH):
            chat_history.pop(0)
        query = event['inputTranscript']
        result = run_chain(qa, query, chat_history)
        chat_history.append((query, result["answer"]))
        final_response.append(result["answer"].split('\n')[0])
        # print(result["answer"].split('\n')[0])
        if 'source_documents' in result:
            for d in result['source_documents']:
                final_response.append(d.metadata['source'])
        response = ''
        for resp in final_response:
            if len(response) > 0:
                response = response + '\n' + resp
            else:
                response = resp
        return {
            "sessionState": {
                "dialogAction": {
                    "slotElicitationStyle": "Default",
                    "slotToElicit": "string",
                    "type": "Close"
                },
                "intent": {
                    "confirmationState": "None",
                    "name": lex_search_intent_name,
                    "slots": {},
                    "state": "Fulfilled"
                }
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": response
                }
            ],
            "requestAttributes": {}
        }
    except Exception as ex:
        logger.debug('bot.generated.exception={}'.format(ex))
        return {
            "sessionState": {
                "dialogAction": {
                    "slotElicitationStyle": "Default",
                    "slotToElicit": "string",
                    "type": "Close"
                },
                "intent": {
                    "confirmationState": "None",
                    "name": lex_search_intent_name,
                    "slots": {},
                    "state": "Fulfilled"
                }
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "Sorry, no information available!"
                }
            ],
            "requestAttributes": {}
        }

def lambda_handler(event, context):
    return dispatch_intent(event)

if __name__ == "__main__":
    event = {
        "inputTranscript": "Who is the CEO of Air Products?",
        "sessionId": "686768716876871",
        "bot": {
            "name": "anthropic.claude_v2"
        }
    }
    print(lambda_handler(event, None))