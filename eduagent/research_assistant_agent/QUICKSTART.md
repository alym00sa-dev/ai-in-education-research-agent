# Quick Start Guide

Get your Research Assistant running in 5 minutes!

## ✅ Pre-flight Checklist

Make sure you have:
- [x] Neo4j Aura instance (you have this!)
- [x] OpenAI API key
- [x] Anthropic API key
- [x] Tavily API key
- [x] Open Deep Research backend ready

## 🚀 Step 1: Test Your Setup (2 minutes)

```bash
cd /Users/alymoosa/Downloads/LangChain-Agent/research_assistant

# Test Neo4j connection
python test_neo4j.py
# Should see: ✅ Successfully connected to Neo4j!

# Initialize taxonomy nodes
python init_database.py
# Should see: ✅ Database ready! with node counts
```

## 🔬 Step 2: Start Backend (1 minute)

Open a new terminal:

```bash
cd /Users/alymoosa/Downloads/LangChain-Agent/open_deep_research

# Start LangGraph backend
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

Wait for:
```
🚀 API: http://127.0.0.1:2024
```

## 🎨 Step 3: Start Streamlit (1 minute)

Open another new terminal:

```bash
cd /Users/alymoosa/Downloads/LangChain-Agent/research_assistant

# Start the app
streamlit run app.py
```

Browser should auto-open to `http://localhost:8501`

## 🧪 Step 4: Run Your First Research (5 minutes)

In the Streamlit UI:

1. **In the sidebar**, click "ITS Effectiveness" preset query
2. **At the top**, keep defaults:
   - Model: openai:gpt-4.1
   - Depth: standard
   - Focus: All Education Topics
3. **Click "🚀 Start Research"**
4. **Wait 3-5 minutes** ☕
5. **See results!**
   - Research summary
   - Papers added
   - Interactive knowledge graph

## 🎉 Success Indicators

You should see:

- ✅ "Research complete!" message
- ✅ "Papers Added: 3-8" metric
- ✅ Interactive graph with colored nodes
- ✅ Expandable paper list
- ✅ Session appears in sidebar history

## 🐛 Quick Troubleshooting

**If you see "Connection refused to Neo4j":**
```bash
python test_neo4j.py
# Fix your .env file if needed
```

**If you see "No response from LangGraph":**
```bash
curl http://127.0.0.1:2024/ok
# Restart the LangGraph backend if needed
```

**If research takes >10 minutes:**
- This is normal for "deep" or "comprehensive" depth
- Use "standard" for faster results (3-5 min)

## 📝 What to Try Next

1. **Ask a follow-up question** (same session)
2. **Start a new research chat** (new session)
3. **Load a past session** from sidebar
4. **Try different presets** to build your knowledge graph
5. **View cumulative graph** showing connections across topics

## 🔍 Verify Your Knowledge Graph

In Neo4j Browser (if you want to explore):

```cypher
// See all nodes
MATCH (n) RETURN labels(n) as type, count(n) as count

// See your papers
MATCH (p:Paper) RETURN p.title, p.session_id

// See implementation → outcome patterns
MATCH (io:ImplementationObjective)-[r:TARGETS_OUTCOME]->(o:Outcome)
RETURN io.type, o.name, r.weight
ORDER BY r.weight DESC
```

## 💡 Pro Tips

- **First query takes longest** (downloads papers, extracts metadata)
- **Subsequent queries are cumulative** (graph grows)
- **Use preset queries** for best results (they're tuned for tutoring research)
- **Sessions persist** - you can revisit them anytime
- **Graph shows patterns** - look for thick edges (common connections)

## 📚 Next Steps

- Read `PIPELINE.md` to understand the workflow
- Check `SCHEMA.md` for knowledge graph structure
- See `README.md` for advanced usage

---

**Need help?** Check the Troubleshooting section in README.md
