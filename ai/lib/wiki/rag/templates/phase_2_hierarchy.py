phase_2_hierarchy_template = """
The given context represents the structure of a Wikipedia page or several Wikipedia pages in Python dict form.
The keys at the top level represent the Wikipedia page titles, and the corresponding values are the hierarchical structure of the page.

**Objective**: Given the question and the provided page hierarchy(s), select the most relevant path or paths that likely contain the answer. Create a JSON object using schema provided below.

THE PATH OR PATHS SHOULD STRICTLY DERIVE FROM THE HIERARCHY STRUCTURE PROVIDED IN THE CONTEXT. DO NOT MAKE UP NEW PATHS. 
STRICTLY FOLLOW THE SCHEMA: 

{{hierarchy_path_schema}}

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
