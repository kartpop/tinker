### Should be encapsulated in a function for reuse
# Parametrize the function for flexibility

## v2: uses WikiContextCreatorV2 instead of WikiContextCreator

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wiki.api.lib.components.wiki_hierarchy_builder import WikiHierarchyBuilder
from wiki.api.lib.components.wiki_context_creator_v2 import WikiContextCreatorV2
from wiki.api.lib.templates import hierarchy_template, p2_qa_template_v2
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from haystack import Pipeline

wiki_hierarchy_builder = WikiHierarchyBuilder(
    "bolt://localhost:7687", "neo4j", "neo4jpass"
)
hierarchy_prompt_builder = PromptBuilder(template=hierarchy_template)
hierarchy_generator = OpenAIGenerator(model="gpt-4o-mini")
elasticsearch_store = ElasticsearchDocumentStore(hosts="http://localhost:9200")
wiki_context_creator = WikiContextCreatorV2(document_store=elasticsearch_store)
p2_qa_prompt_builder = PromptBuilder(template=p2_qa_template_v2)
p2_qa_generator = OpenAIGenerator(model="gpt-4o-mini")


graph_pipeline = Pipeline()

graph_pipeline.add_component("wiki_hierarchy_builder", wiki_hierarchy_builder)
graph_pipeline.add_component("hierarchy_prompt_builder", hierarchy_prompt_builder)
graph_pipeline.add_component("hierarchy_generator", hierarchy_generator)
graph_pipeline.add_component("wiki_context_creator", wiki_context_creator)
graph_pipeline.add_component("p2_qa_prompt_builder", p2_qa_prompt_builder)
graph_pipeline.add_component("p2_qa_generator", p2_qa_generator)

graph_pipeline.connect(
    "wiki_hierarchy_builder.sections_hierarchy", "hierarchy_prompt_builder.hierarchy"
)
graph_pipeline.connect("hierarchy_prompt_builder", "hierarchy_generator")
graph_pipeline.connect(
    "hierarchy_generator.replies", "wiki_context_creator.hierarchy_paths"
)
graph_pipeline.connect(
    "wiki_hierarchy_builder.chunks_hierarchy", "wiki_context_creator.chunks_hierarchy"
)
graph_pipeline.connect(
    "wiki_context_creator.documents", "p2_qa_prompt_builder.documents"
)
graph_pipeline.connect("p2_qa_prompt_builder", "p2_qa_generator")
