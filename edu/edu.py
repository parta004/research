# https://documentation.you.com/api-reference/research

# Use deep research API to get structured timeline

# Request
# import requests

# url = "https://chat-api.you.com/research"
# https://you.com/search?q=Hi%2C+can+you+please+research+what+events+led+to+Russian+x+Ukraine+war+%3F+In+terms+of+economical+and+military+activities+%3F&fromSearchBar=true&cid=c0_0a48844c-edb0-4304-ad2e-2ba285edf186

# payload = {
#     "query": "<string>",
#     "chat_id": "3c90c3cc-0d44-4b50-8888-8dd25736052a"
# }
# headers = {
#     "X-API-Key": "<api-key>",
#     "Content-Type": "application/json"
# }

# response = requests.request("POST", url, json=payload, headers=headers)

# print(response.text)

# Response schema
# {
#   "answer": "# The Impact of AI on Productivity\n\nArtificial Intelligence (AI) is increasingly becoming a pivotal force in enhancing productivity across various sectors. ",
#   "search_results": [
#     {
#       "url": "https://www.goldmansachs.com/insights/articles/AI-is-showing-very-positive-signs-of-boosting-gdp#:~:text=concerns%20about%20privacy%20and,of%20the%20technology%20as",
#       "name": "AI is showing very positive signs of eventually boosting GDP and productivity",
#       "snippet": "2024-05-13 | the net impact on the labor market has been positive thus far..."
#     }
#   ]
# }


# B - Firecrawl for Deep Research
# from firecrawl import FirecrawlApp

# # Initialize the client
# firecrawl = FirecrawlApp(api_key="your_api_key")


# # Start research with real-time updates
# def on_activity(activity):
#     print(f"[{activity['type']}] {activity['message']}")

# # Run deep research
# results = firecrawl.deep_research(
#     query="What are the latest developments in quantum computing?",
#     max_depth=5,
#     time_limit=180,
#     max_urls=15,
#     on_activity=on_activity
# )

# # Access research findings.
# print(f"Final Analysis: {results['data']['finalAnalysis']}")

# print(f"Sources: {len(results['data']['sources'])} references")
