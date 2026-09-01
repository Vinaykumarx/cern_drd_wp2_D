import re

def recursive_chunk_text(text, max_chars=1000, overlap=200):
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    if not text:
        return []

    # Heuristic splitters in order of preference
    separators = ["\n\n", "\n", "(?<=[.?!]) +", " "]
    
    def split_with_sep(text_to_split, sep):
        if sep.startswith("(?<="):
            return re.split(sep, text_to_split)
        return text_to_split.split(sep)

    def recursive_split(text_to_split, sep_idx):
        if len(text_to_split) <= max_chars:
            return [text_to_split]
            
        if sep_idx >= len(separators):
            # Fallback: force split by chunks of max_chars
            return [text_to_split[i:i+max_chars] for i in range(0, len(text_to_split), max_chars)]
            
        sep = separators[sep_idx]
        splits = split_with_sep(text_to_split, sep)
        
        # If the separator didn't split anything, try the next one
        if len(splits) == 1:
            return recursive_split(text_to_split, sep_idx + 1)
            
        final_chunks = []
        for s in splits:
            if s:
                final_chunks.extend(recursive_split(s, sep_idx + 1))
        return final_chunks

    pieces = recursive_split(text, 0)
    
    # Merge pieces into chunks
    chunks = []
    current_chunk = []
    current_len = 0
    
    for piece in pieces:
        piece_len = len(piece)
        if current_len + piece_len + 1 > max_chars and current_chunk:
            chunk_str = " ".join(current_chunk)
            chunks.append(chunk_str)
            
            # Backtrack for overlap
            overlap_words = []
            overlap_len = 0
            for w in reversed(current_chunk):
                if overlap_len + len(w) + 1 > overlap:
                    break
                overlap_words.insert(0, w)
                overlap_len += len(w) + 1
            current_chunk = overlap_words
            current_len = overlap_len
            
        current_chunk.append(piece)
        # Adding 1 for the space that join will add
        current_len += piece_len + 1
        
    if current_chunk:
        chunk_str = " ".join(current_chunk)
        if len(chunk_str.strip()) > 30:
            chunks.append(chunk_str)
            
    return chunks

sample = "This is a sentence. This is another sentence! What about this one? This is a very long sentence that has many words and will probably exceed the limit if the limit is very small."
print(recursive_chunk_text(sample, max_chars=50, overlap=10))
