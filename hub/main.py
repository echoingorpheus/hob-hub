from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import redis, os, json, uuid

app = FastAPI(title="Holon Hub")
# --- singletons -------------------------------------------------
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
)
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))
redis_pub = redis.from_url(os.getenv("REDIS_URL"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")
# ---------------------------------------------------------------

class StorePayload(BaseModel):
    block: str = Field(..., description="7‑line Holonic block")

@app.post("/store", status_code=201)
def store(payload: StorePayload):
    try:
        objects = parse_blocks(payload.block)
    except ValueError as e:
        raise HTTPException(400, str(e))

    with neo4j_driver.session() as ses:
        for obj in objects:
            _merge_neo4j(ses, obj)
            _upsert_qdrant(obj)
            redis_pub.publish("object.stored", json.dumps({"id": obj["id"], "type": obj["type"]}))
    return {"stored": len(objects)}

# ---------------- helpers --------------------------------------
from .parser import parse_blocks           # tests cover this
def _merge_neo4j(session, obj):
    q = "MERGE (n:Holon {marker:$m}) SET n.moniker=$moniker, n.type=$t, n.nature=$n"
    session.run(q, m=obj["marker"], moniker=obj["moniker"], t=obj["type"], n=obj["nature"])
    # relations omitted for brevity

def _upsert_qdrant(obj):
    vec = embedder.encode(obj["nature"] or obj["moniker"])
    qdrant.upsert(
        collection_name="holons",
        points=[(uuid.uuid4().hex, vec.tolist(), {"marker": obj["marker"], "type": obj["type"]})],
    )