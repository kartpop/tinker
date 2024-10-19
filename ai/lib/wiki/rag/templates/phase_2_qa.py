phase_2_qa_template = """
Answer the question using the following context. Try not use any external information. 

If the answer is only partially covered, provide the partial answer and mention explicitly that it may be incomplete.

**Answer only using below schema. Include the document IDs from which the answer is extracted. Each document in the given context starts with '---- Document <doc_index> ----'. The document ID should be the value of <doc_index>.**

THE ANSWER SCHEMA SHOULD BE STRICTLY FOLLOWED. DO NOT CHANGE THE ANSWER SCHEMA.

{{phase_2_qa_schema}}

### Example:
----------------------------------------

Context:

---- Document 1 ----
.........some text......

---- Document 2 ----
.........some text......

---- Document 3 ----
.........some text......

Question:
Write a short essay on the paleobiology of dinosaurs?

Answer:
{
  "answer": <generated-short-essay>,
  "document_ids": [2, 3]
}

----------------------------------------


Context:
{% for document in documents %}
    ---- Document {{ loop.index }} ----
    {{ document.content }}
{% endfor %}

Question: {{query}}

Answer: {{phase_2_qa_schema}}
"""
