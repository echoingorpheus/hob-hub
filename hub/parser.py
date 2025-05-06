import re
def parse_blocks(text:str):
    blocks = [b for b in text.strip().split("\n\n") if b.strip()]
    results=[]
    for block in blocks:
        lines = block.rstrip().split("\n")
        if len(lines)!=7:
            raise ValueError("Each block must have 7 lines (incl. blank separator).")
        name,nature,typeline,partof,haspart,rel,_ = lines
        if not name.strip() or not typeline.strip():
            raise ValueError("Name and type lines required.")
        # split marker vs moniker
        if ":" in name:
            marker, moniker = name.split(":",1)
            marker = marker.strip()+":"
            moniker=moniker.strip()
        else:
            marker, moniker = name.strip(),""
        type_word,*tag_parts = re.split(r"\s+`?\s*",typeline.strip(" `"))
        tags=[t.strip() for t in tag_parts if t]
        obj={"id":marker+moniker,"marker":marker,"moniker":moniker,
             "nature":nature.replace("`","\n").strip(),
             "type":type_word,"tags":tags}
        # TODO: parse relations via back‑ticks
        results.append(obj)
    return results