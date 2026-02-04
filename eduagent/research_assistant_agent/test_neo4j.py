"""Quick test script to verify Neo4j connection."""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")
database = os.getenv("NEO4J_DATABASE", "neo4j")

print(f"Testing Neo4j connection...")
print(f"URI: {uri}")
print(f"User: {user}")
print(f"Database: {database}")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✅ Successfully connected to Neo4j!")

    # Test a simple query
    with driver.session(database=database) as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()
        print(f"✅ Test query successful: {record['test']}")

    driver.close()
    print("\n🎉 Neo4j is ready to use!")

except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Neo4j is running")
    print("2. Check your credentials in .env")
    print("3. Verify the URI is correct (bolt://localhost:7687)")
