"""Quick diagnostic script to check and clean stale reminders in ChromaDB."""
import chromadb

c = chromadb.PersistentClient(path="./chroma_db")
col = c.get_or_create_collection("deepclaw_memory")

reminders = col.get(where={"type": "reminder"})

print(f"\n=== Found {len(reminders['ids'])} pending reminder(s) ===\n")

for i in range(len(reminders["ids"])):
    doc_id = reminders["ids"][i]
    meta = reminders["metadatas"][i]
    doc = reminders["documents"][i]
    print(f"  [{i+1}] ID: {doc_id}")
    print(f"      Text: {doc}")
    print(f"      Meta: {meta}")
    print()

# Clean all stale reminders
if reminders["ids"]:
    print("Cleaning all stale reminders...")
    col.delete(ids=reminders["ids"])
    print(f"Deleted {len(reminders['ids'])} stale reminder(s). Done!")
else:
    print("No stale reminders to clean. DB is clean!")
