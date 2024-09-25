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
The following context represents the structure of a Wikipedia page in Python dict form, including the title, h2, h3, and h4 sections.

**Objective**: Given the question and the provided page hierarchy, select the most relevant section or path that likely contains the answer.

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
**Dinosaur -> Overview -> Etymology**  
**Reasoning**: The word's meaning is likely to be explained in the "Etymology" section.

If the question is broad, like "Give an overview of dinosaurs," you can respond:
**Dinosaur -> Overview**  
**Reasoning**: The "Overview" section is designed to provide a broad summary.

### Context:
{{hierarchy}}

### Question:
{{query}}

### Response:
Path: <your-selected-path-or-paths>
Reasoning: <your-reasoning>
"""


final_template = """
Answer the question only using the following context. Do not use any external information. If the answer is not present in the context, respond with "I don't know." If the answer is only partially covered, provide the partial answer and mention explicitly that it may be incomplete.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{query}}
Answer (note if partial):
"""
