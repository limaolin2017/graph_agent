"""
Simplified database and semantic search test script - Single Store + PGVector version
"""

import asyncio
from database import db, search_artifacts_advanced

async def quick_test():
    """Quickly test database connection and semantic search - Single Store version"""
    print("🔍 Quickly testing single store + pgvector...")

    # Test database connection
    await db.connect()
    print("✅ Database connection successful")

    # Test saving artifacts
    test_content = "This is a test login page with username and password input fields"
    success = await db.save_artifact("test_run_001", "scrape", test_content, "https://test.example.com/login", "Test login page", "scrape_url")
    if success:
        print("✅ Artifact saved successfully")
    else:
        print("❌ Failed to save artifact")
        return False

    # Test semantic search
    results = search_artifacts_advanced("login test", k=3)
    print(f"✅ Semantic search completed, found {len(results)} results")

    # Display search results
    for i, result in enumerate(results[:2]):  # Only show first 2 results
        print(f"  Result {i+1}: {result.get('summary', 'No summary')[:50]}...")

    await db.close()
    return True

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    print("🎉 Test completed" if success else "❌ Test failed")
