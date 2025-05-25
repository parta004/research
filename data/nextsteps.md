# TBD top50
## Props
- cateogry mimo result item 
- number of items (validated by BE as well)
- time period - enum (Year, Decade, All time)
- use search (app will decide)
- user specification TBD


## LLM
- Provide sorting criteria
- Sport: Main team
- Game: Genre
- Movie: Genre
- Music: Genre

- stats mapovat hard pro každou subkategorii zvlášť

## Movie
- description remove
- genre - one main only
- order/priority
- rating
- awards object - something main only - 4 types of awards and structured output

## Sports
- Task prompt should be more free
- creator:blank to remove
- year: to remove for players
- description: to remove from all
- group_tag: only one - describe majority of carier or most known for
- awards: naštudovat pro fotbal, hokej, basket zvlášť

## Music
- Proposed grouping - group
- image avatar optional zavézt, ale ne hudba

# What to do
- Co dál, vyzkoušet všechny 3 typy prommptů dnes
- Vytvořit službu pro single item
- Vyzkoušet search

1. Start with Brave, DuckduckGo as backup
- Create wrapper for all three providers and test today

```python
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools.brave_search.tool import BraveSearch
from langchain.chat_models import ChatOpenAI

# Step 1: Load LLM and Search Tool
llm = ChatOpenAI(temperature=0, model="gpt-4")
brave_tool = BraveSearch(api_key="YOUR_BRAVE_API_KEY", search_kwargs={"count": 10})

# Step 2: Initialize Agent with the Tool
agent = initialize_agent(
    tools=[brave_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Step 3: Ask the Agent
query = "Get a structured list of the top 50 NBA players of all time with their teams"
response = agent.run(query)

print(response)

```
- Na serper potřeba registrace

