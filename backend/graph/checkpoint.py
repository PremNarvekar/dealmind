from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

from config import DATABASE_URL


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": True,
    },
)

checkpointer = PostgresSaver(pool)

checkpointer.setup()