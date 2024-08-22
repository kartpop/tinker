from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from fastapi import FastAPI
from pydantic import BaseModel


class Question(BaseModel):
    text: str


def ask_question(question: str) -> str:
    template = """Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return response.content


app = FastAPI()


@app.post("/ask")
async def ask(q: Question):
    return {"response": ask_question(q.text)}
