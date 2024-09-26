starter_template = """
Answer the question using **only** the provided context. Do not use any external information beyond the context below.

### Context:
{% for document in documents %}
    ---- Document {{ loop.index }} ----
    {{ document.content }}
{% endfor %}

### Guidelines for Your Answer:
Your answer should be one of the following:
1. **Actual Answer**: Provide this if the answer is **clearly present** in the context.
    - Ensure your response is concise and directly relevant to the query.

2. **"need_more_context"**: Choose this if the question is **too broad, subjective, or the context is insufficient** to provide a definitive answer.

### Question:
{{ query }}

### Answer:
"""


hierarchy_template = """
The given context represents the structure of a Wikipedia page or several Wikipedia pages in Python dict form.
The keys at the top level represent the Wikipedia page titles, and the corresponding values are the hierarchical structure of the page.

**Objective**: Given the question and the provided page hierarchy(s), select the most relevant path or paths that likely contain the answer. Create a JSON object using schema provided below.

### Key Guidelines:
- Your response should trace the hierarchy to the section that best answers the question.
- You may not need to go to the lowest level of the hierarchy. For broad questions, selecting a higher-level section is appropriate.
- If the answer could be present across multiple sections, select the section that is most directly related to the query, or provide multiple sections if necessary.
- Please include a brief reasoning for your choice of section(s).

### Example:
For the Wikipedia page titled "Dinosaur" with the structure:
{
    "title": "Dinosaur",
    "sections": [
        {
            "name": "Overview",
            "type": "h2",
            "sections": [
                {
                    "name": "Etymology",
                    "type": "h3"
                }
            ]
        }
    ]
}

If the question is: "What does the word dinosaur mean?", respond:
{
  "paths": [
    {
      "path": ["Dinosaur", "Overview", "Etymology"],
      "reasoning": "The word's meaning is likely to be explained in the \"Etymology\" section."
    }
  ]
}

If the question is broad, like "Give an overview of dinosaurs," you can respond:
{
  "paths": [
    {
      "path": ["Dinosaur", "Overview"],
      "reasoning": "The \"Overview\" section is designed to provide a broad summary."
    }
  ]
}

If multiple sections are relevant to a given question, you can provide multiple paths. For example, for the question "Give an overview of dinosaurs' distinguishing features and sizes" you could respond:
{
  "paths": [
    {
      "path": ["Dinosaur", "Definition", "Distinguishing anatomical features"],
      "reasoning": "Distinguishing features are likely to be discussed in this section."
    },
    {
      "path": ["Dinosaur", "Paleobiology", "Size"],
      "reasoning": "An overview of dinosaur sizes is likely to be found in this section."
    }
  ]
}

### Context:
{{hierarchy}}

### Question:
{{query}}

### Response:
{{hierarchy_path_schema}}
"""


final_template = """
Answer the question only using the following context. Do not use any external information. If the answer is not present in the context, respond with "I don't know." If the answer is only partially covered, provide the partial answer and mention explicitly that it may be incomplete.

Context:
{% for document in context_list %}
    ---- Document {{ loop.index }} ----
    {{ document }}
{% endfor %}

Question: {{query}}
Answer (note if partial):
"""
