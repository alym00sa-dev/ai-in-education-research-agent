"""Deep Researcher — graph definition and compilation.

To add a new research phase, create a file in nodes/ and wire it in here.

Current workflow:
    clarify_with_user → write_research_brief → research_supervisor → qa_review → swanson_abc → final_report_generation
"""

from langgraph.graph import END, START, StateGraph

from configuration import Configuration
from state import AgentInputState, AgentState
from nodes.clarify import clarify_with_user
from nodes.brief import write_research_brief
from nodes.supervisor import supervisor_subgraph
from nodes.qa import qa_review
from nodes.swanson import swanson_abc
from nodes.report import final_report_generation


deep_researcher_builder = StateGraph(
    AgentState,
    input=AgentInputState,
    config_schema=Configuration
)

deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)
deep_researcher_builder.add_node("qa_review", qa_review)
deep_researcher_builder.add_node("swanson_abc", swanson_abc)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)

deep_researcher_builder.add_edge(START, "clarify_with_user")
deep_researcher_builder.add_edge("research_supervisor", "qa_review")
deep_researcher_builder.add_edge("qa_review", "swanson_abc")
deep_researcher_builder.add_edge("swanson_abc", "final_report_generation")
deep_researcher_builder.add_edge("final_report_generation", END)

deep_researcher = deep_researcher_builder.compile()
