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

## Sports
- Task prompt should be more free
- group_tag: only one - describe majority of carier or most known for
- awards: naštudovat pro fotbal, hokej, basket zvlášť

# Factchecking
- Offline analysis
## 1. Data source strategy

- **Government APIs:** Integrate official APIs (BLS for employment, Census Bureau, Fed Reserve, CDC, etc.)

- **Academic Databases:** Use APIs from FRED (Federal Reserve Economic Data), World Bank, IMF

- **Specialized Search Operators:** Craft queries targeting .gov, .edu domains and PDF reports

- **Time-Series Analysis:** Track how statistics change over time to detect cherry-picking

```python
statistical_queries = [
    f'site:bls.gov "{keyword}" filetype:pdf',
    f'site:census.gov {metric} {year} data',
    f'"{exact_statistic}" source methodology'
]
```

### Key Considerations
- **Temporal Context:** Always get historical data to see if a claim uses selective timeframes
- **Methodology Verification:** Find the actual survey/study methodology
- **Margin of Error:** Look for confidence intervals and sample sizes
- **Seasonal Adjustments:** Check if data is seasonally adjusted when relevant

## 2. Source credibility strategy
- **Source Diversity Score:** Count unique domains, not just mentions
- **Cross-Reference Matrix:** Track which sources cite which other sources
- **Temporal Distribution:** When did sources first report this? (identifies original vs. echo chamber)
- **Geographic Distribution:** Are sources from different regions/countries?

### Advanced technique
- **Citation Network Analysis:** Build a graph of who cites whom
- **Fact-Check Aggregation:** Check multiple fact-checking organizations
- **Academic Consensus:** Use Google Scholar API to find academic papers
- **Media Bias Ratings:** Integrate AllSides or Media Bias/Fact Check ratings

## 3. Recognize media manipulation:

```python
manipulation_indicators = {
    "timing_patterns": [
        "coordinated release across multiple outlets",
        "story breaks just before important events",
        "Friday news dumps"
    ],
    "framing_techniques": [
        "emotional language density",
        "passive vs active voice usage",
        "buried corrections",
        "misleading headlines vs. article content"
    ],
    "statistical_tricks": [
        "baseline shifting",
        "cherry-picked date ranges",
        "absolute numbers vs. percentages",
        "correlation presented as causation"
    ]
}
```

1. **Semantic Similarity Analysis:**
- Detect when multiple outlets use identical phrasing
- Identify talking points distribution
- Track narrative evolution

2. **Image/Video Verification:**
- Reverse image search for context
- Check EXIF data when available
- Look for deepfake indicators


3. **Source Chain Analysis:**
- Track the "telephone game" of citations
- Identify circular reporting
- Find the original source vs. amplifiers


### Red Flags to Automate Detection For:

- **Coordinated Messaging:** Multiple sources using identical unusual phrases
- **Missing Context:** Statistics without denominators or comparisons
- **Emotional Manipulation:** High density of fear/anger/outrage words
- **False Urgency:** "Breaking" news about non-urgent matters
- **Astroturfing:** Fake grassroots movements with suspicious funding

## 4. Enhanced research

```python
research_stages = {
    "stage_1": "Broad search for claims and counter-claims",
    "stage_2": "Deep dive into primary sources",
    "stage_3": "Statistical verification",
    "stage_4": "Bias and manipulation analysis",
    "stage_5": "Historical context check"
}
```

### Suggested tools
- **APIs:** Google Scholar, CrossRef, ArXiv, PubMed
- **Fact-Check APIs:** Google Fact Check Tools API, ClaimReview schema
- **Statistical Sources:** Quandl, DataUSA, OECD Stats
- **Media Analysis:** GDELT Project, MediaCloud

```python
def calculate_statement_reliability(sources):
    score = 0
    score += len(tier_1_sources) * 3
    score += len(tier_2_sources) * 2
    score -= len(tier_4_sources) * 1
    score += geographic_diversity_bonus
    score += temporal_consistency_bonus
    score -= manipulation_indicators_penalty
    return normalize_score(score)
```

## 5. Implementation 
- Caching locally
- Rate Limiting
- Fallback Chains
- Confidence Intervals: Never present findings as absolute truth
- Audit Trail: Keep detailed logs of all sources checked