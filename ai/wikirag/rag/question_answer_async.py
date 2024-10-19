import asyncio
import json
import logging
from lib.wiki.rag.helpers.log_helpers import custom_serializer, strip_embeddings_from_dict
from lib.wiki.rag.models.hierarchy_path import HierarchyPathData
from lib.wiki.rag.models.phase_2_qa import Phase2QA
from lib.wiki.rag.pipelines.graph_pipeline import GraphPipeline
from lib.wiki.rag.pipelines.hybrid_pipeline import HybridPipeline
from lib.wiki.rag.models.phase_1_qa import Phase1QA


class QuestionAnswerAsync:
    def __init__(self, hybrid_pipeline: HybridPipeline, graph_pipeline: GraphPipeline, logger: logging.Logger):
        self.hybrid_pipeline = hybrid_pipeline.build()
        self.graph_pipeline = graph_pipeline.build()
        self.logger = logger

    async def run_sync(self, func, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

    async def question_answer(self, question: str) -> dict:
        """
        Runs the RAG pipeline to answer the given question.

        First invokes the hybrid pipeline to generate an answer. If the answer is incomplete and needs more context,
        invokes the graph pipeline to generate the complete answer.
        """
        phase_1_qa_schema = Phase1QA.model_json_schema()

        input_data = {
            "elasticsearch_retriever": {"query": question},
            "text_embedder": {"text": question},
            "phase_1_qa_prompt_builder": {
                "phase_1_qa_schema": phase_1_qa_schema,
                "query": question,
            },
        }

        self.logger.debug("Running hybrid pipeline")

        hybrid_result_dict = await self.run_sync(
            self.hybrid_pipeline.run,
            input_data,
            {
                "text_embedder",
                "weaviate_retriever",
                "elasticsearch_retriever",
                "reciprocal_rank_fusion_joiner",
                "phase_1_qa_prompt_builder",
                "phase_1_qa_generator",
            },
        )

        self.logger.debug("Hybrid pipeline completed, result: %s", strip_embeddings_from_dict(hybrid_result_dict))

        hybrid_replies_json = hybrid_result_dict["phase_1_qa_generator"]["replies"][0]
        hybrid_replies_dict = json.loads(hybrid_replies_json)
        hybrid_replies = Phase1QA(**hybrid_replies_dict)

        if not hybrid_replies.need_more_context:
            # If the answer is complete, return
            answer = {"text": hybrid_replies_json, "phase": 1}
            context_docs = hybrid_result_dict["reciprocal_rank_fusion_joiner"][
                "documents"
            ]
            metadata = {"phase_1": hybrid_result_dict}
            return {
                "answer": answer,
                "context_docs": context_docs,
                "metadata": metadata,
            }
        else:
            # If the answer is incomplete and needs more context, run graph pipeline
            grounding_docs = hybrid_result_dict["reciprocal_rank_fusion_joiner"][
                "documents"
            ]

            path_schema = HierarchyPathData.model_json_schema()
            phase_2_qa_schema = Phase2QA.model_json_schema()

            input_data = {
                "hierarchy_prompt_builder": {
                    "query": question,
                    "hierarchy_path_schema": path_schema,
                },
                "wiki_hierarchy_builder": {"documents": grounding_docs},
                "phase_2_qa_prompt_builder": {
                    "phase_2_qa_schema": phase_2_qa_schema,
                    "query": question,
                },
            }
            
            self.logger.debug("Running graph pipeline")

            try:
                result = await self.run_sync(
                    self.graph_pipeline.run,
                    input_data,
                    {
                        "wiki_hierarchy_builder",
                        "hierarchy_prompt_builder",
                        "hierarchy_generator",
                        "wiki_context_creator",
                        "phase_2_qa_prompt_builder",
                        "phase_2_qa_generator",
                    },
                )
            except Exception as e:
                self.logger.error(f"\nGraph pipeline run failed, find error details below after Phase-1 results.")
                strip_embeddings_from_dict(hybrid_result_dict)
                self.logger.info(f"\nPhase-1 results: {json.dumps(hybrid_result_dict, default=custom_serializer, indent=4)}")
                raise
            
            self.logger.debug("Graph pipeline completed, result: %s", strip_embeddings_from_dict(result))

            answer = {"text": result["phase_2_qa_generator"]["replies"][0], "phase": 2}
            context_docs = result["wiki_context_creator"]["documents"]
            metadata = {"phase-1": hybrid_result_dict, "phase-2": result}
            return {
                "answer": answer,
                "context_docs": context_docs,
                "metadata": metadata,
            }

    async def build_answer_with_reference(
        self, answer: dict, context_docs: dict
    ) -> dict:
        """
        Extracts the answer and references from the given answer object.
        """

        def build_metadata_for_doc(doc):
            metadata = {}
            for key in ["title", "h2", "h3", "h4"]:
                if key in doc.meta and doc.meta[key] is not None:
                    metadata[key] = doc.meta[key]
            return metadata

        phase = answer["phase"]
        answer_json = json.loads(answer["text"])

        if phase == 1:
            answer_obj = Phase1QA(**answer_json)
        else:
            answer_obj = Phase2QA(**answer_json)

        used_doc_ids = answer_obj.document_ids
        references = []
        for doc_id in used_doc_ids:
            ref_doc = context_docs[
                doc_id - 1
            ]  # ref-1 because the document ids are 1-indexed
            references.append(build_metadata_for_doc(ref_doc))
        return {"text": answer_obj.answer, "references": references}

    async def ask(self, question: str) -> dict:
        """
        Runs the RAG pipeline to answer the given question and returns the answer with references.

        Metadata includes the complete pipeline outputs from both phases.

        Example:
        {
            "answer": {
                "text": "Answer text",
                "references": [
                    {
                        "title": "Page Title",
                        "h2": "Section 1",
                        "h3": "Subsection 1",
                        "h4": "Sub-subsection 1"
                    }
                ]
            },
            "metadata": {
                "phase-1": {
                    "text_embedder": {...},
                    "weaviate_retriever": {...},
                    "elasticsearch_retriever": {...},
                    "reciprocal_rank_fusion_joiner": {...},
                    "phase_1_qa_prompt_builder": {...},
                    "phase_1_qa_generator": {...}
                },
                "phase-2": {
                    "wiki_hierarchy_builder": {...},
                    "hierarchy_prompt_builder": {...},
                    "hierarchy_generator": {...},
                    "wiki_context_creator": {...},
                    "phase_2_qa_prompt_builder": {...},
                    "phase_2_qa_generator": {...}
                }
            }
        }
        """
        qa_response = await self.question_answer(question)
        answer_with_reference = await self.build_answer_with_reference(
            qa_response["answer"], qa_response["context_docs"]
        )
        return {"answer": answer_with_reference, "metadata": qa_response["metadata"]}
