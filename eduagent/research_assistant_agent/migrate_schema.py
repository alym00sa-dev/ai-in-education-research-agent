"""
Neo4j Schema Migration Script

This script migrates the existing Neo4j schema to:
1. Convert Population, UserType, StudyDesign from nodes to Paper properties
2. Fix any 'has_synthesis' relationships to 'TARGETS_OUTCOME'
3. Clean up orphaned taxonomy nodes after migration

Run this ONCE to update existing data.
"""

from src.neo4j_config import get_neo4j_connection


def migrate_schema():
    """Migrate existing Neo4j data to new schema."""
    conn = get_neo4j_connection()

    with conn.driver.session(database=conn.database) as session:
        print("🔄 Starting schema migration...\n")

        # Step 1: Copy taxonomy data to Paper properties
        print("📝 Step 1: Converting taxonomy nodes to Paper properties...")

        # Migrate Population
        result = session.run("""
            MATCH (p:Paper)-[:TARGETS_POPULATION]->(pop:Population)
            SET p.population = pop.type
            RETURN count(p) as count
        """)
        pop_count = result.single()['count']
        print(f"   ✅ Migrated {pop_count} Population relationships to properties")

        # Migrate UserType
        result = session.run("""
            MATCH (p:Paper)-[:TARGETS_USER_TYPE]->(ut:UserType)
            SET p.user_type = ut.type
            RETURN count(p) as count
        """)
        ut_count = result.single()['count']
        print(f"   ✅ Migrated {ut_count} UserType relationships to properties")

        # Migrate StudyDesign
        result = session.run("""
            MATCH (p:Paper)-[:USES_STUDY_DESIGN]->(sd:StudyDesign)
            SET p.study_design = sd.type
            RETURN count(p) as count
        """)
        sd_count = result.single()['count']
        print(f"   ✅ Migrated {sd_count} StudyDesign relationships to properties")

        # Step 2: Delete old relationships
        print("\n🗑️  Step 2: Deleting old taxonomy relationships...")

        result = session.run("""
            MATCH (p:Paper)-[r:TARGETS_POPULATION]->()
            DELETE r
            RETURN count(r) as count
        """)
        print(f"   ✅ Deleted {result.single()['count']} TARGETS_POPULATION relationships")

        result = session.run("""
            MATCH (p:Paper)-[r:TARGETS_USER_TYPE]->()
            DELETE r
            RETURN count(r) as count
        """)
        print(f"   ✅ Deleted {result.single()['count']} TARGETS_USER_TYPE relationships")

        result = session.run("""
            MATCH (p:Paper)-[r:USES_STUDY_DESIGN]->()
            DELETE r
            RETURN count(r) as count
        """)
        print(f"   ✅ Deleted {result.single()['count']} USES_STUDY_DESIGN relationships")

        # Step 3: Fix 'has_synthesis' relationships to 'TARGETS_OUTCOME'
        print("\n🔧 Step 3: Fixing 'has_synthesis' relationships...")

        # First, check if any exist
        result = session.run("""
            MATCH ()-[r:has_synthesis]->()
            RETURN count(r) as count
        """)
        synthesis_count = result.single()['count']

        if synthesis_count > 0:
            # Fix them
            result = session.run("""
                MATCH (io:ImplementationObjective)-[old:has_synthesis]->(out:Outcome)
                MERGE (io)-[new:TARGETS_OUTCOME]->(out)
                ON CREATE SET new.weight = 1
                ON MATCH SET new.weight = COALESCE(new.weight, 0) + 1
                DELETE old
                RETURN count(old) as count
            """)
            print(f"   ✅ Fixed {result.single()['count']} has_synthesis relationships")
        else:
            print(f"   ℹ️  No has_synthesis relationships found")

        # Step 4: Clean up orphaned taxonomy nodes (optional)
        print("\n🧹 Step 4: Checking for orphaned taxonomy nodes...")

        # Count orphaned Population nodes
        result = session.run("""
            MATCH (pop:Population)
            WHERE NOT (pop)<-[:TARGETS_POPULATION]-()
            RETURN count(pop) as count
        """)
        orphaned_pop = result.single()['count']

        # Count orphaned UserType nodes
        result = session.run("""
            MATCH (ut:UserType)
            WHERE NOT (ut)<-[:TARGETS_USER_TYPE]-()
            RETURN count(ut) as count
        """)
        orphaned_ut = result.single()['count']

        # Count orphaned StudyDesign nodes
        result = session.run("""
            MATCH (sd:StudyDesign)
            WHERE NOT (sd)<-[:USES_STUDY_DESIGN]-()
            RETURN count(sd) as count
        """)
        orphaned_sd = result.single()['count']

        total_orphaned = orphaned_pop + orphaned_ut + orphaned_sd

        if total_orphaned > 0:
            print(f"   ℹ️  Found {total_orphaned} orphaned taxonomy nodes")
            print(f"      Population: {orphaned_pop}, UserType: {orphaned_ut}, StudyDesign: {orphaned_sd}")
            print(f"   ℹ️  Keeping them for now (can be deleted manually if desired)")
        else:
            print(f"   ✅ No orphaned nodes found")

        # Step 5: Verify migration
        print("\n✅ Step 5: Verifying migration...")

        # Check that papers have properties
        result = session.run("""
            MATCH (p:Paper)
            WHERE p.population IS NOT NULL
            RETURN count(p) as count
        """)
        papers_with_pop = result.single()['count']

        result = session.run("""
            MATCH (p:Paper)
            RETURN count(p) as total
        """)
        total_papers = result.single()['total']

        print(f"   📊 {papers_with_pop}/{total_papers} papers have population property")
        print(f"   📊 Total papers in database: {total_papers}")

        # Show sample paper
        result = session.run("""
            MATCH (p:Paper)
            WHERE p.population IS NOT NULL
            RETURN p.title as title,
                   p.population as population,
                   p.user_type as user_type,
                   p.study_design as study_design
            LIMIT 1
        """)
        sample = result.single()
        if sample:
            print(f"\n   📄 Sample migrated paper:")
            print(f"      Title: {sample['title'][:60]}...")
            print(f"      Population: {sample['population']}")
            print(f"      UserType: {sample['user_type']}")
            print(f"      StudyDesign: {sample['study_design']}")

        print("\n🎉 Migration complete!")
        print("\nℹ️  Next steps:")
        print("   1. Run a test query in research_assistant/app.py")
        print("   2. Verify new papers use the updated schema")
        print("   3. Optionally delete orphaned taxonomy nodes if desired")


if __name__ == "__main__":
    try:
        migrate_schema()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
