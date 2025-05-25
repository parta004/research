# How to ADK
## 1. Sequential agent
Use sequence which will force the serialized step procedure at start. This will avoid fucking up message distribution between multiple agents

## 2. State management strategy
before_agent_callback, after_agent_callback
- Use these methods for context passing

input_schema, output_schema
- Force schemas if possible on both sides to achieve more consistent results 

