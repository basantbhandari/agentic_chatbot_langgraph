docker run --name postgres-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=langgraph \
  -p 5432:5432 \
  -d pgvector/pgvector:pg16
