def print_neatly(text, max_len=55):
    """
    Splits a long string into a list of strings, each not exceeding max_len.
    Tries to split at spaces to avoid breaking words.
    """
    if not text:
        return [""]
    
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        temp_line = ' '.join(current_line + [word])
        if len(temp_line) <= max_len:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(' '.join(current_line))
        
    return lines