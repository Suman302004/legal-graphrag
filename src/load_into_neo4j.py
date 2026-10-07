import pandas as pd
from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
# ============================================================

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"

# IMPORTANT:
# Replace this with the password you set for your Neo4j database.
PASSWORD = "Suman@9699"

DATABASE = "neo4j"

CASES_FILE = "data/cases.csv"
RELATIONSHIPS_FILE = "data/resolved_relationships.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading case data...")
    cases = pd.read_csv(CASES_FILE)

    print(f"Cases loaded: {len(cases)}")

    print("\nLoading relationship data...")
    relationships = pd.read_csv(RELATIONSHIPS_FILE)

    print(f"Relationships loaded: {len(relationships)}")

    return cases, relationships


# ============================================================
# CREATE CASE NODES
# ============================================================

def create_case_nodes(tx, cases):

    query = """
    UNWIND $cases AS case

    MERGE (c:Case {case_id: case.case_id})

    SET c.title = case.title,
        c.citation = case.citation,
        c.judge = case.judge,
        c.author_judge = case.author_judge,
        c.decision_date = case.decision_date,
        c.court = case.court,
        c.path = case.path

    RETURN count(c) AS count
    """

    result = tx.run(
        query,
        cases=cases
    )

    return result.single()["count"]


# ============================================================
# CREATE LEGAL RELATIONSHIPS
# ============================================================

def create_relationships(tx, relationships):

    query = """
    UNWIND $relationships AS rel

    MATCH (source:Case {case_id: rel.source_case_id})
    MATCH (target:Case {case_id: rel.target_case_id})

    MERGE (source)-[r:$(rel.relationship)]->(target)

    SET r.citations = rel.citations,
        r.resolution_method = rel.resolution_method,
        r.resolved_using = rel.resolved_using

    RETURN count(r) AS count
    """

    result = tx.run(
        query,
        relationships=relationships
    )

    return result.single()["count"]


# ============================================================
# MAIN
# ============================================================

def main():

    # Load CSV files
    cases_df, relationships_df = load_data()

    # Convert NaN / NA values to None
    cases_df = cases_df.where(pd.notnull(cases_df), None)
    relationships_df = relationships_df.where(
        pd.notnull(relationships_df),
        None
    )

    # Convert DataFrames to dictionaries
    cases = cases_df.to_dict("records")
    relationships = relationships_df.to_dict("records")

    # Connect to Neo4j
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        # Verify connection
        driver.verify_connectivity()

        print("\nConnected to Neo4j successfully.")

        with driver.session(database=DATABASE) as session:

            # ------------------------------------------------
            # REMOVE OLD GRAPH
            # ------------------------------------------------

            print("\nClearing existing graph...")

            session.run("""
                MATCH (n)
                DETACH DELETE n
            """)

            print("Existing graph cleared.")

            # ------------------------------------------------
            # CREATE CASE NODES
            # ------------------------------------------------

            print("\nCreating case nodes...")

            session.execute_write(
                create_case_nodes,
                cases
            )

            print("Case nodes created.")

            # ------------------------------------------------
            # CREATE RELATIONSHIPS
            # ------------------------------------------------

            print("\nCreating legal relationships...")

            session.execute_write(
                create_relationships,
                relationships
            )

            print("Relationships created.")

        print("\n===================================")
        print("NEO4J GRAPH IMPORT COMPLETE")
        print("===================================")
        print(f"Nodes: {len(cases)}")
        print(f"Relationships: {len(relationships)}")

    finally:

        driver.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()