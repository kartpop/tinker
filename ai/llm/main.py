from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from fastapi import FastAPI
from pydantic import BaseModel
import requests


class Question(BaseModel):
    question: str


def ask_question(context: str, question: str) -> str:
    template = """Answer the question based only on the following context:
    {context}
    
    If response has sections, headings, bullet points etc. respond in markdown
    format, else respond in plain text.

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

    chain = prompt | llm

    response = chain.invoke({"context": context, "question": question})

    return response.content


app = FastAPI()


@app.post("/ask")
async def ask(q: Question):

    response = requests.get(
        "http://localhost:5728/articles",
        params={"prompt": q.question, "percentile": 0.5, "num_results": 1},
    )
    response_json = response.json()
    context = response_json[0]["text"]
    title = response_json[0]["title"]

    json_data = {"response": ask_question(context, q.question), "wiki_title": title}
    print(json_data)
    return json_data
