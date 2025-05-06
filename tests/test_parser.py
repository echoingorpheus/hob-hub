from hub.parser import parse_blocks

BLOCK = """
C’1: Orpheus
Legendary poet.
symbol ` musician ` poet
C.a ` C.A
C’2

"""

def test_minimal_block():
    res = parse_blocks(BLOCK)
    assert res[0]["marker"]=="C’1:"
    assert res[0]["type"]=="symbol"