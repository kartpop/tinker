## Phase-1 templates

# Phase-1 question answer template
p1_qa_template = """
Answer the question using **only** the provided context. Do not use any external information beyond the context below. Answer only using below schema.

### Key Guidelines:
The answer schema has three fields:
1. anwser: The answer to the question. Try to answer the question in the best possible manner using the context **even if you set 'need_more_context' to true**, BUT **do not use external information**. 
2. need_more_context: A boolean value indicating whether the context is sufficient to answer the question. If the context is not sufficient, set this field to true. 
  - **You can set this field to true even if you have answered the question partially using the context.**
  - Only set this field to false if the context clearly provides the answer and the question is direct and specific. Before setting this field to false, ensure that the question has been answered in full.
3. reasoning: If you set `need_more_context` to true, provide a brief reasoning explaining why the context is insufficient to answer the question. If you set `need_more_context` to false, provide a brief reasoning explaining how the context answers the question **in full without missing any parts of question**.

### Examples (only questions and answers are shown here, context will be provided in the actual task):
----------------------------------------

Question:
When did dinosaurs first appear?

Answer:
{
  "answer": "Dinosaurs first appeared during the Triassic period, between 243 and 233.23 million years ago.",
  "need_more_context": false,
  "reasoning": "The context clearly states the time period when dinosaurs first appeared."
}

----------------------------------------

Question:
What caused the extinction of dinosaurs?

Answer:
{
  "answer": "",
  "need_more_context": true,
  "reasoning": "The context does not provide information about the causes of dinosaur extinction."
}

----------------------------------------

Question:
Give a brief about the anatomical features of dinosaurs and their size.

Answer:
{
  "answer": "Dinosaurs exhibited a variety of anatomical features, including modifications to the ancestral archosaurian skeleton and elaborate display structures such as horns or crests. Some groups developed skeletal modifications like bony armor and spines. Dinosaurs varied significantly in size; while many were large-bodied, such as the largest sauropods reaching lengths of 39.7 meters and heights of 18 meters, many were quite small, measuring about 50 centimeters in length.",
  "need_more_context": true,
  "reasoning": "The context provides some information about the anatomical features and size of dinosaurs, but it may not cover all aspects of the question."
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


## Phase-2 templates

# Phase-2 hierarchy template
p2_hierarchy_template = """
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

# Phase-2 question answer template
p2_qa_template = """
Answer the question only using the following context. Do not use any external information. If the answer is not present in the context, respond with "I don't know." If the answer is only partially covered, provide the partial answer and mention explicitly that it may be incomplete.

Context:
{% for document in context_list %}
    ---- Document {{ loop.index }} ----
    {{ document }}
{% endfor %}

Question: {{query}}
Answer (note if partial):
"""


## ----------DEPRECATED TEMPLATES----------

# Phase-2 hierarchy template
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

# Phase-2 question answer template
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
