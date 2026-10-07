from neo4j import GraphDatabase


# ==========================================
# NEO4J CONFIGURATION
# ==========================================

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Suman@9699"


# ==========================================
# CONNECT TO NEO4J
# ==========================================

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# ==========================================
# GET RELATED CASES
# ==========================================

def get_related_cases(case_id):

    query = """
    MATCH (source:Case {case_id: $case_id})
          -[r]->(target:Case)

    RETURN
        source.case_id AS source_case_id,
        source.title AS source_title,
        type(r) AS relationship,
        target.case_id AS target_case_id,
        target.title AS target_title,
        target.citation AS target_citation

    ORDER BY target.case_id
    """

    with driver.session() as session:

        result = session.run(
            query,
            case_id=case_id
        )

        records = []

        for record in result:
            records.append({
                "source_case_id": record["source_case_id"],
                "source_title": record["source_title"],
                "relationship": record["relationship"],
                "target_case_id": record["target_case_id"],
                "target_title": record["target_title"],
                "target_citation": record["target_citation"]
            })

        return records


# ==========================================
# GET CASE DETAILS
# ==========================================

def get_case(case_id):

    query = """
    MATCH (c:Case {case_id: $case_id})

    RETURN
        c.case_id AS case_id,
        c.title AS title,
        c.citation AS citation,
        c.judge AS judge,
        c.decision_date AS decision_date,
        c.court AS court
    """

    with driver.session() as session:

        result = session.run(
            query,
            case_id=case_id
        )

        record = result.single()

        if record is None:
            return None

        return {
            "case_id": record["case_id"],
            "title": record["title"],
            "citation": record["citation"],
            "judge": record["judge"],
            "decision_date": record["decision_date"],
            "court": record["court"]
        }


# ==========================================
# BUILD GRAPH CONTEXT
# ==========================================

def build_graph_context(case_id):

    case = get_case(case_id)

    if case is None:
        return None

    related_cases = get_related_cases(case_id)

    return {
        "case": case,
        "related_cases": related_cases
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("Connected to Neo4j successfully.")

    case_id = "2025 INSC 24"

    context = build_graph_context(case_id)

    print("\n===================================")
    print("GRAPH CONTEXT")
    print("===================================")

    if context is None:

        print("Case not found.")

    else:

        case = context["case"]

        print("\nMAIN CASE")
        print("-----------------------------------")
        print("Case ID:", case["case_id"])
        print("Title:", case["title"])
        print("Citation:", case["citation"])
        print("Judge:", case["judge"])
        print("Decision Date:", case["decision_date"])
        print("Court:", case["court"])

        print("\nRELATED CASES")
        print("-----------------------------------")

        for related in context["related_cases"]:

            print(
                f"{related['relationship']} → "
                f"{related['target_case_id']}"
            )

            print(
                f"Title: {related['target_title']}"
            )

            print(
                f"Citation: {related['target_citation']}"
            )

            print("-----------------------------------")

    driver.close()