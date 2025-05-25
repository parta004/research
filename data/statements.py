
# Test data
## List of statemets

### 1. Historical statements - No web research needed, LLM knowledge sufficient to response. Goal: Verify thinking process and output structure of agents
obama_laden = """
"Bin Laden is dead, and General Motors is alive."
"""
# 2012 campaign slogan, should be generally evaluated as true
## Bin Laden was killed in 2011
## GM received a bailout in 2009 and returned to profitability in 2010

trump_rate = """
"The crime rate in the U.S. is the highest it’s been in 47 years."
"""

# Tweet 2017
## Early 90s was the highest crime rate in the US

merkel_euro = """
"The euro is much more than a currency. It is the symbol of European unity and integration."
"""
# Speech 2010
## Euro was introduced in 1999, and it has been a symbol of European unity since then, but the statement is subjective and can be debated.
## Not an empirical statement, but rather a political one.


boris_brexit = """
"We send the EU £350 million a week."
"""

## 2016 Brexit campaign bus
# The figure is misleading as it does not account for the UK's rebate and other financial contributions to the EU budget.

putin_crimea = """
"There are no Russian troops in Crimea."
"""
# Response to international concerns
## Russia annexed Crimea in 2014, and there were indeed Russian troops present, despite the denial.

### 2. Present statements - Web research needed
st_biden_cancer = """
Former President Joe Biden has been diagnosed with prostate cancer. The type of cancer he has is considered "aggressive," but is it also "turbo," as some on social media have said? 
"It is sad to see another one who is Covid vaccinated and boosted it to the hilt, get turbo cancer already metastasized,"
"""
# Input improvements
## Chybí kontext - kdy, odkud, kdo ... dodat celý statement ve formě objektu 

#  Suggested output{
#   "statement": "[Original Quote]",
#   "speaker": "[Person's name]",opinions
#   "date": "[Approx. date]",
#   "context": "[Brief explanation of the political context]",
#   "verdict": "True / False / Misleading / Unverifiable",
#   "reasoning": "[How the LLM or agent arrived at the verdict]",
#   "": [
#     "Fact 1",
#     "Fact 2",
#     ...
#   ]
# }