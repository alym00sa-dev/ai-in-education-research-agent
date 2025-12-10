"""Initialize the Neo4j database with taxonomy nodes."""
from src.neo4j_config import initialize_database

if __name__ == "__main__":
    print("🚀 Initializing Neo4j database...")
    initialize_database()
    print("\n✅ Database ready!")
