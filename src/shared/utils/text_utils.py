from typing import List

def chunk_text(text: str, max_chars: int = 10000) -> List[str]:
    """
    Splits text into chunks of at most max_chars length.
    Tries to split on paragraphs first, then newlines, then spaces to avoid breaking words.
    """
    if not text:
        return []
        
    if len(text) <= max_chars:
        return [text]
        
    chunks = []
    current_chunk = ""
    
    # Split by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        # If adding this paragraph exceeds max, save current chunk and start new
        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # If the paragraph itself is too huge, we need to split it further
            if len(para) > max_chars:
                # Split by single lines
                lines = para.split('\n')
                for line in lines:
                     if len(current_chunk) + len(line) + 1 > max_chars:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = ""
                        
                        # If line is still too huge, hard split
                        if len(line) > max_chars:
                             # This is a very rare case (a single line > 30k chars), just hard chunk
                             for i in range(0, len(line), max_chars):
                                 chunks.append(line[i:i+max_chars])
                        else:
                            current_chunk += line + "\n"
                     else:
                        current_chunk += line + "\n"
            else:
                current_chunk += para + "\n\n"
        else:
            current_chunk += para + "\n\n"
            
    if current_chunk:
        chunks.append(current_chunk)
        
    # Clean up whitespace
    return [c.strip() for c in chunks if c.strip()]
