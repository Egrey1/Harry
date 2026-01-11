from .modules import match

async def increment_iteration(text: str) -> str:
    pattern = r'(.*?)(\d+)/(\d+)\s+(\d+)(.*)'
    matchh = match(pattern, text)
    
    if not matchh:
        return text
    
    prefix, current_str, total_str, year_str, suffix = matchh.groups()
    current = int(current_str)
    total = int(total_str)
    year = int(year_str)
    
    current += 1
    if current > total:
        current = 1
        year += 1
    
    return f"{prefix}{current}/{total} {year}{suffix}"