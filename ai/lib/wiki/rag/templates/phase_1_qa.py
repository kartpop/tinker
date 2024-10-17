phase_1_qa_template = """
Answer the question using **only** the provided context. Do not use any external information beyond the context below. Answer only using below schema.

### Key Guidelines:
The answer schema has four fields:
1. anwser: The answer to the question. Try to answer the question in the best possible manner using the context **even if you set 'need_more_context' to true**, BUT **do not use external information**. 
2. need_more_context: A boolean value indicating whether the context is sufficient to answer the question. If the context is not sufficient, set this field to true. 
  - **You can set this field to true even if you have answered the question partially using the context.**
  - Only set this field to false if the context clearly provides the answer and the question is direct and specific. Before setting this field to false, ensure that the question has been answered in full.
3. reasoning: If you set `need_more_context` to true, provide a brief reasoning explaining why the context is insufficient to answer the question. If you set `need_more_context` to false, provide a brief reasoning explaining how the context answers the question **in full without missing any parts of question**.
4. document_ids: List of unique identifiers of the document or documents from which the answer is extracted. Each document in the given context starts with '---- Document <doc_index> ----'. The document_id should be the value of <doc_index>.

### Examples (only questions and answers are shown here, context will be provided in the actual task):
----------------------------------------

Question:
When did dinosaurs first appear?

Answer:
{
  "answer": "Dinosaurs first appeared during the Triassic period, between 243 and 233.23 million years ago.",
  "need_more_context": false,
  "reasoning": "The context clearly states the time period when dinosaurs first appeared."
  "document_ids": [1]
}

----------------------------------------

Question:
What caused the extinction of dinosaurs?

Answer:
{
  "answer": "",
  "need_more_context": true,
  "reasoning": "The context does not provide information about the causes of dinosaur extinction."
  "document_ids": []
}

----------------------------------------

Question:
Give a brief about the anatomical features of dinosaurs and their size.

Answer:
{
  "answer": "Dinosaurs exhibited a variety of anatomical features, including modifications to the ancestral archosaurian skeleton and elaborate display structures such as horns or crests. Some groups developed skeletal modifications like bony armor and spines. Dinosaurs varied significantly in size; while many were large-bodied, such as the largest sauropods reaching lengths of 39.7 meters and heights of 18 meters, many were quite small, measuring about 50 centimeters in length.",
  "need_more_context": true,
  "reasoning": "The context provides some information about the anatomical features and size of dinosaurs, but it may not cover all aspects of the question."
  "document_ids": [1, 2]
}

----------------------------------------


### Context:
{% for document in documents %}
    ---- Document {{ loop.index }} ----
    {{ document.content }}
{% endfor %}

### Question:
{{ query }}

### Answer:
{{p1_qa_schema}}
"""
