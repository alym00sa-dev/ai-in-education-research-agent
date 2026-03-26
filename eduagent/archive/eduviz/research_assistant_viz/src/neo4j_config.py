"""Neo4j configuration and taxonomy initialization."""
import os
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()

# Fixed taxonomies from build_kg_csvs.py
POPULATIONS = [
    "Elementary (PreK-5th)",
    "Middle School (6th-8th)",
    "High School (9th-12th)",
    "Undergraduate",
    "Graduate",
    "Adult"
]

USER_TYPES = [
    "Student",
    "Educator",
    "Administrator",
    "Parent",
    "School",
    "Community",
    "Systematic: social/political level information"
]

STUDY_DESIGNS = [
    "Randomized Control Trial",
    "Quasi-Experimental Design",
    "Meta-Analysis/Systematic Review",
    "Mixed-Methods Study",
    "Qualitative Study"
]

IMPLEMENTATION_OBJECTIVES = [
    "Intelligent Tutoring and Instruction",
    "AI-Enable Personalized Advising",
    "Institutional Decision-making",
    "AI-Enabled Learner Mobility"
]

OUTCOMES = [
    "Cognitive - Critical Thinking/Metacognitive skills",
    "Cognitive - Reading and writing literacy",
    "Cognitive - speaking, listening, and language fluency",
    "Cognitive - Mathematical numeracy",
    "Cognitive - Scientific Reasoning",
    "Behavioral - task and assignment efficiency",
    "Behavioral - study habits, concentration",
    "Behavioral - participation and social engagement",
    "Behavioral - productivity",
    "Affective - motivation",
    "Affective - engagement",
    "Affective - persistence"
]

FINDING_DIRECTIONS = ["Positive", "Negative", "No Effect", "Mixed"]


class Neo4jConnection:
    """Manages Neo4j database connection and operations."""

    def __init__(self):
        """Initialize Neo4j connection from environment variables."""
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver: Optional[Driver] = None

    def connect(self) -> Driver:
        """Establish connection to Neo4j."""
        if not self.driver:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
        return self.driver

    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """Execute a Cypher query."""
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def create_indexes(self):
        """Create indexes for faster query performance."""
        print("Creating database indexes...")

        with self.driver.session(database=self.database) as session:
            # Create indexes for faster lookups
            indexes = [
                "CREATE INDEX IF NOT EXISTS FOR (p:Paper) ON (p.title)",
                "CREATE INDEX IF NOT EXISTS FOR (io:ImplementationObjective) ON (io.id)",
                "CREATE INDEX IF NOT EXISTS FOR (o:Outcome) ON (o.id)",
                "CREATE INDEX IF NOT EXISTS FOR (pop:Population) ON (pop.id)",
                "CREATE INDEX IF NOT EXISTS FOR (ut:UserType) ON (ut.id)",
                "CREATE INDEX IF NOT EXISTS FOR (sd:StudyDesign) ON (sd.id)"
            ]

            for index_query in indexes:
                try:
                    session.run(index_query)
                except Exception as e:
                    print(f"  Index creation warning: {e}")

        print("✅ Indexes created!")

    def initialize_taxonomies(self):
        """Create all taxonomy nodes if they don't exist."""
        print("Initializing taxonomy nodes...")

        with self.driver.session(database=self.database) as session:
            # Population nodes
            for pop in POPULATIONS:
                session.run(
                    """
                    MERGE (p:Population {id: $id, type: $type})
                    """,
                    id=pop, type=pop
                )

            # UserType nodes
            for ut in USER_TYPES:
                session.run(
                    """
                    MERGE (u:UserType {id: $id, type: $type})
                    """,
                    id=ut, type=ut
                )

            # StudyDesign nodes
            for sd in STUDY_DESIGNS:
                session.run(
                    """
                    MERGE (s:StudyDesign {id: $id, type: $type})
                    """,
                    id=sd, type=sd
                )

            # ImplementationObjective nodes
            for io in IMPLEMENTATION_OBJECTIVES:
                session.run(
                    """
                    MERGE (i:ImplementationObjective {id: $id, type: $type})
                    """,
                    id=io, type=io
                )

            # Outcome nodes
            for outcome in OUTCOMES:
                session.run(
                    """
                    MERGE (o:Outcome {id: $id, name: $name})
                    """,
                    id=outcome, name=outcome
                )

        print("✅ Taxonomy nodes initialized!")

    def clear_database(self):
        """DANGER: Clear all nodes and relationships. Use with caution!"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("⚠️  Database cleared!")

    def get_node_counts(self) -> Dict[str, int]:
        """Get counts of all node types."""
        query = """
        MATCH (n)
        RETURN labels(n)[0] as label, count(n) as count
        ORDER BY label
        """
        results = self.execute_query(query)
        return {r['label']: r['count'] for r in results if r['label']}


# Singleton instance
_connection: Optional[Neo4jConnection] = None


def get_neo4j_connection() -> Neo4jConnection:
    """Get or create the Neo4j connection singleton."""
    global _connection
    if _connection is None:
        _connection = Neo4jConnection()
        _connection.connect()
    return _connection


def initialize_database():
    """Initialize database with taxonomies and indexes (safe to run multiple times)."""
    conn = get_neo4j_connection()
    conn.create_indexes()
    conn.initialize_taxonomies()
    print("\n📊 Current node counts:")
    for label, count in conn.get_node_counts().items():
        print(f"  {label}: {count}")
