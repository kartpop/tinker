from lib.wiki.rag.components.wiki_hierarchy_builder import WikiHierarchyBuilder
from lib.wiki.rag.components.wiki_context_creator import WikiContextCreator
from lib.wiki.rag.templates.phase_2_hierarchy import phase_2_hierarchy_template
from lib.wiki.rag.templates.phase_2_qa import phase_2_qa_template
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from haystack import Pipeline


class PipelineSingleton:
    """
    In Haystack, each component instance can only be used in a single pipeline. This singleton class ensures that the
    component instances are only used in a single pipeline.
    """

    _instance = None

    @classmethod
    def get_instance(cls, build_func):
        if cls._instance is None:
            cls._instance = build_func()
        return cls._instance
    
class GraphPipeline:
    """
    A RAG pipeline for question answering. 
    
    Phase-2: Attempts to build a more comprehensive context from the Phase-1 context which are the smaller document chunks. Graph database
    is used to first zoom into the chunk nodes and then traverse the hierarchy to build a more comprehensive context. 
    The context is then fed to the LLM to generate the answer.
    """
    def __init__(
        self,
        wiki_hierarchy_builder: WikiHierarchyBuilder,
        hierarchy_prompt_builder: PromptBuilder,
        hierarchy_generator: OpenAIGenerator,
        elasticsearch_store: ElasticsearchDocumentStore,
        wiki_context_creator: WikiContextCreator,
        phase_2_qa_prompt_builder: PromptBuilder,
        phase_2_qa_generator: OpenAIGenerator,
    ):
        self.wiki_hierarchy_builder = wiki_hierarchy_builder
        self.hierarchy_prompt_builder = hierarchy_prompt_builder
        self.hierarchy_generator = hierarchy_generator
        self.elasticsearch_store = elasticsearch_store
        self.wiki_context_creator = wiki_context_creator
        self.phase_2_qa_prompt_builder = phase_2_qa_prompt_builder
        self.phase_2_qa_generator = phase_2_qa_generator

    def build(self)-> Pipeline:
        """
        Builds a haystack pipeline which does the following:
        1. Builds wikipedia page hierarchy(ies) corresponding to the given document chunks using a graph database.
        2. Invokes an LLM to generate the most likely section path(s) of the hierarchy which may contain the answer. eg. Page Title > Section 1 > Subsection 1.3
        3. Recreates the wikipedia section(s) text from the LLM generated path(s) and the document chunks.
        4. Feeds the comprehensive wikipedia section(s) text as context to the LLM to generate the answer to the question.
        """
        def create_pipeline() -> Pipeline:
            pipeline = Pipeline()
            pipeline.add_component("wiki_hierarchy_builder", self.wiki_hierarchy_builder)
            pipeline.add_component(
                "hierarchy_prompt_builder", self.hierarchy_prompt_builder
            )
            pipeline.add_component("hierarchy_generator", self.hierarchy_generator)
            pipeline.add_component("wiki_context_creator", self.wiki_context_creator)
            pipeline.add_component(
                "phase_2_qa_prompt_builder", self.phase_2_qa_prompt_builder
            )
            pipeline.add_component("phase_2_qa_generator", self.phase_2_qa_generator)

            pipeline.connect(
                "wiki_hierarchy_builder.sections_hierarchy",
                "hierarchy_prompt_builder.hierarchy",
            )
            pipeline.connect("hierarchy_prompt_builder", "hierarchy_generator")
            pipeline.connect(
                "hierarchy_generator.replies", "wiki_context_creator.hierarchy_paths"
            )
            pipeline.connect(
                "wiki_hierarchy_builder.chunks_hierarchy",
                "wiki_context_creator.chunks_hierarchy",
            )
            pipeline.connect(
                "wiki_context_creator.documents", "phase_2_qa_prompt_builder.documents"
            )
            pipeline.connect("phase_2_qa_prompt_builder", "phase_2_qa_generator")

            return pipeline
        
        return PipelineSingleton.get_instance(create_pipeline)
