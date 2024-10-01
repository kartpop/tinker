from lib.components.wiki_hierarchy_builder import WikiHierarchyBuilder
from lib.components.wiki_context_creator import WikiContextCreator
from lib.templates import hierarchy_template, final_template
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
wiki_context_creator = WikiContextCreator(document_store=elasticsearch_store)
final_prompt_builder = PromptBuilder(template=final_template)
final_generator = OpenAIGenerator(model="gpt-4o-mini")


graph_pipeline = Pipeline()

graph_pipeline.add_component("wiki_hierarchy_builder", wiki_hierarchy_builder)
graph_pipeline.add_component("hierarchy_prompt_builder", hierarchy_prompt_builder)
graph_pipeline.add_component("hierarchy_generator", hierarchy_generator)
graph_pipeline.add_component("wiki_context_creator", wiki_context_creator)
graph_pipeline.add_component("final_prompt_builder", final_prompt_builder)
graph_pipeline.add_component("final_generator", final_generator)

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
    "wiki_context_creator.context_list", "final_prompt_builder.context_list"
)
graph_pipeline.connect("final_prompt_builder", "final_generator")
