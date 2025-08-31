import re
import json


"""
    Input: raw agent output (dict or string)
    Output: Returns the best-effort merged result
    Functionality: Extract and merge any JSON block from the summary string into the dict
"""
def parse_agent_output(raw_result):
    
    if isinstance(raw_result, dict) and 'output' in raw_result:
        text = raw_result['output']
        # Try to find a JSON block inside "output" as seen by '```json'
        match = re.search(r'```json\s*([\s\S]+?)```', text)
        if match:
            try:
                agent_dict = json.loads(match.group(1))
                raw_result.update(agent_dict)
            except Exception:
                pass
        else:
            match = re.search(r'({[\s\S]+})', text)
            if match:
                try:
                    agent_dict = json.loads(match.group(1))
                    raw_result.update(agent_dict)
                except Exception:
                    pass
    return raw_result