def fallback_node(state):

    state["answer"] = (
        "I can only answer questions related to the current report."
    )

    return state