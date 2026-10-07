from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
# ============================================================

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"

# CHANGE THIS to your Neo4j password
PASSWORD = "Suman@9699"

DATABASE = "neo4j"


# ============================================================
# NEO4J CONNECTION
# ============================================================

class LegalGraph:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

    def close(self):
        self.driver.close()

    def verify_connection(self):
        self.driver.verify_connectivity()
        print("Connected to Neo4j successfully.")


    # ========================================================
    # GET ALL CASES
    # ========================================================

    def get_all_cases(self):

        query = """
        MATCH (c:Case)
        RETURN
            c.case_id AS case_id,
            c.title AS title,
            c.citation AS citation,
            c.judge AS judge,
            c.decision_date AS decision_date,
            c.court AS court
        ORDER BY c.decision_date
        """

        with self.driver.session(database=DATABASE) as session:

            result = session.run(query)

            return [record.data() for record in result]


    # ========================================================
    # GET CASE BY ID
    # ========================================================

    def get_case(self, case_id):

        query = """
        MATCH (c:Case {case_id: $case_id})
        RETURN
            c.case_id AS case_id,
            c.title AS title,
            c.citation AS citation,
            c.judge AS judge,
            c.decision_date AS decision_date,
            c.court AS court,
            c.path AS path
        """

        with self.driver.session(database=DATABASE) as session:

            result = session.run(
                query,
                case_id=case_id
            )

            record = result.single()

            if record:
                return record.data()

            return None


    # ========================================================
    # GET CASE RELATIONSHIPS
    # ========================================================

    def get_related_cases(self, case_id):

        query = """
        MATCH (source:Case {case_id: $case_id})
              -[r]->
              (target:Case)

        RETURN
            source.case_id AS source_case_id,
            type(r) AS relationship,
            target.case_id AS target_case_id,
            target.title AS target_title,
            target.citation AS target_citation
        """

        with self.driver.session(database=DATABASE) as session:

            result = session.run(
                query,
                case_id=case_id
            )

            return [record.data() for record in result]


    # ========================================================
    # GET CASES BY RELATIONSHIP TYPE
    # ========================================================

    def get_cases_by_relationship(
        self,
        case_id,
        relationship_type
    ):

        query = """
        MATCH (source:Case {case_id: $case_id})
              -[r]->
              (target:Case)

        WHERE type(r) = $relationship_type

        RETURN
            source.case_id AS source_case_id,
            type(r) AS relationship,
            target.case_id AS target_case_id,
            target.title AS target_title,
            target.citation AS target_citation
        """

        with self.driver.session(database=DATABASE) as session:

            result = session.run(
                query,
                case_id=case_id,
                relationship_type=relationship_type
            )

            return [record.data() for record in result]


# ============================================================
# TEST THE GRAPH QUERY LAYER
# ============================================================

def main():

    graph = LegalGraph()

    try:

        # ----------------------------------------------------
        # TEST CONNECTION
        # ----------------------------------------------------

        graph.verify_connection()


        # ----------------------------------------------------
        # TEST 1: GET ALL CASES
        # ----------------------------------------------------

        print("\n===================================")
        print("ALL CASES")
        print("===================================")

        cases = graph.get_all_cases()

        for case in cases:

            print(
                f"{case['case_id']} | "
                f"{case['title']}"
            )


        # ----------------------------------------------------
        # TEST 2: GET SPECIFIC CASE
        # ----------------------------------------------------

        print("\n===================================")
        print("SPECIFIC CASE")
        print("===================================")

        case = graph.get_case("2025 INSC 24")

        print(case)


        # ----------------------------------------------------
        # TEST 3: GET RELATED CASES
        # ----------------------------------------------------

        print("\n===================================")
        print("RELATED CASES")
        print("===================================")

        related = graph.get_related_cases(
            "2025 INSC 24"
        )

        for relationship in related:

            print(
                f"{relationship['relationship']} → "
                f"{relationship['target_case_id']}"
            )


        # ----------------------------------------------------
        # TEST 4: GET ONLY CITED CASES
        # ----------------------------------------------------

        print("\n===================================")
        print("CITED CASES")
        print("===================================")

        cited = graph.get_cases_by_relationship(
            "2025 INSC 24",
            "CITES"
        )

        for relationship in cited:

            print(
                f"{relationship['target_case_id']} | "
                f"{relationship['target_title']}"
            )


    finally:

        graph.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()