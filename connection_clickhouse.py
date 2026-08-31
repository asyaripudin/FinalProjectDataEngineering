import clickhouse_connect

client = clickhouse_connect.get_client(
    host="localhost",
    port=8124,
    username="admin",
    password="ClickHouse@2026",
    database="DataEngineeringDB"
)

result = client.query("SELECT version()")

print("Connected to ClickHouse!")
print("Database:", client.database)
print("ClickHouse version:", result.result_rows[0][0])