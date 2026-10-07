from graph_queries import LegalGraph


# ============================================================
# GRAPH CONTEXT BUILDER
# ============================================================

def build_case_context(graph, case_id):

    # --------------------------------------------------------
    # Get main case
    # --------------------------------------------------------

    case = graph.get_case(case_id)

    if not case:
        return None

    # --------------------------------------------------------
    # Get related cases
    # --------------------------------------------------------

    related_cases = graph.get_related_cases(case_id)

    # --------------------------------------------------------
    # Build readable context
    # --------------------------------------------------------

    context = []

    context.append("MAIN CASE")
    context.append("=" * 60)

    context.append(
        f"Case ID: {case['case_id']}"
    )

    context.append(
        f"Title: {case['title']}"
    )

    context.append(
        f"Citation: {case['citation']}"
    )

    context.append(
        f"Judge: {case['judge']}"
    )

    context.append(
        f"Decision Date: {case['decision_date']}"
    )

    context.append(
        f"Court: {case['court']}"
    )


    # --------------------------------------------------------
    # Related cases
    # --------------------------------------------------------

    context.append("")
    context.append("RELATED CASES")
    context.append("=" * 60)


    if not related_cases:

        context.append(
            "No related cases found."
        )

    else:

        for relation in related_cases:

            context.append(
                f"Relationship: {relation['relationship']}"
            )

            context.append(
                f"Target Case ID: {relation['target_case_id']}"
            )

            context.append(
                f"Target Case: {relation['target_title']}"
            )

            context.append(
                f"Target Citation: {relation['target_citation']}"
            )

            context.append("-" * 60)


    return "\n".join(context)


# ============================================================
# TEST
# ============================================================

def main():

    graph = LegalGraph()

    try:

        graph.verify_connection()

        print("\nBuilding graph context...")

        context = build_case_context(
            graph,
            "2025 INSC 24"
        )

        print("\n")
        print(context)

    finally:

        graph.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()