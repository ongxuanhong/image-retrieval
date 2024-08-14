# image-retrieval

## Chromadb
```python
# Persistent client to store indexed images
chromadb.PersistentClient(path="./chromadb/persisted")
```

```bash
# disk usage (du -ha chromadb)
3.0M    chromadb/persisted/chroma.sqlite3
2.1M    chromadb/persisted/48ddcd3f-5629-4ff1-b28f-e68eff8fa046/data_level0.bin
4.0K    chromadb/persisted/48ddcd3f-5629-4ff1-b28f-e68eff8fa046/length.bin
  0B    chromadb/persisted/48ddcd3f-5629-4ff1-b28f-e68eff8fa046/link_lists.bin
4.0K    chromadb/persisted/48ddcd3f-5629-4ff1-b28f-e68eff8fa046/header.bin
2.1M    chromadb/persisted/48ddcd3f-5629-4ff1-b28f-e68eff8fa046
5.1M    chromadb/persisted
5.1M    chromadb
```