from langgraph.graph import (
    StateGraph,
    END
)

from graph.state import (
    ReportState
)

from agents.feedback_agent import (
    feedback_node
)

from agents.facilities_agent import (
    facilities_node
)

from agents.defect_agent import (
    defect_node
)

from agents.security_agent import (
    security_node
)

from agents.fallback_agent import (
    fallback_node
)

from agents.visitor_management_agent import (
    visitor_management_node
)


# --------------------------------------------------
# Route Based On Current Page Module
# --------------------------------------------------

def route_module(
    state: ReportState
):

    current_module = state.get(
        "current_module",
        ""
    )

    if current_module == "feedback":

        return "feedback"

    elif current_module == "facilities":

        return "facilities"

    elif current_module == "visitor":

        return "visitor"

    elif current_module == "defect":

        return "defect"

    elif current_module == "security":

        return "security"

    return "fallback"


# --------------------------------------------------
# Start Node
# --------------------------------------------------

def start_node(
    state: ReportState
):

    return state


# --------------------------------------------------
# Graph Definition
# --------------------------------------------------

workflow = StateGraph(
    ReportState
)

workflow.add_node(
    "start",
    start_node
)

workflow.add_node(
    "feedback",
    feedback_node
)

workflow.add_node(
    "facilities",
    facilities_node
)

workflow.add_node(
    "visitor",
    visitor_management_node
)

workflow.add_node(
    "defect",
    defect_node
)

workflow.add_node(
    "security",
    security_node
)

workflow.add_node(
    "fallback",
    fallback_node
)

# --------------------------------------------------
# Entry Point
# --------------------------------------------------

workflow.set_entry_point(
    "start"
)

# --------------------------------------------------
# Route To Correct Agent
# --------------------------------------------------

workflow.add_conditional_edges(
    "start",
    route_module,
    {
        "feedback": "feedback",
        "facilities": "facilities",
        "visitor": "visitor",
        "defect": "defect",
        "security": "security",
        "fallback": "fallback"
    }
)

# --------------------------------------------------
# End Nodes
# --------------------------------------------------

workflow.add_edge(
    "feedback",
    END
)

workflow.add_edge(
    "facilities",
    END
)

workflow.add_edge(
    "visitor",
    END
)

workflow.add_edge(
    "defect",
    END
)

workflow.add_edge(
    "security",
    END
)

workflow.add_edge(
    "fallback",
    END
)

# --------------------------------------------------
# Compile Graph
# --------------------------------------------------

graph = workflow.compile()


# --------------------------------------------------
# Public Function
# --------------------------------------------------

def run_report_graph(
    property_id: str,
    period: str,
    question: str,
    current_module: str,
    authorization: str
) -> str:

    result = graph.invoke(
        {
            "property_id": property_id,
            "period": period,
            "question": question,
            "current_module": current_module,
            "authorization": authorization,
            "answer": ""
        }
    )

    return result.get(
        "answer",
        "No response generated."
    )