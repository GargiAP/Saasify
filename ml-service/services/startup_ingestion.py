from database.startup_repository import create_startup, startup_exists
from database.vector_repository import save_vector
from services.embedder import generate_embedding


def ingest_startup(startup):

    if startup_exists(startup["name"]):
        print(f"Skipped: {startup['name']} already exists")
        return

    response = create_startup(startup)

    startup_id = response.data[0]["id"]

    embedding_text = f"""
    {startup.get('name', '')}
    {startup.get('description', '')}
    {' '.join(startup.get('tags', []))}
    """

    vector = generate_embedding(
        embedding_text
    )

    save_vector(
        startup_id=startup_id,
        vector=vector,
        payload={
            "name": startup["name"],
            "source": startup.get(
                "source",
                ""
            )
        }
    )

    print(
        f"Inserted: {startup['name']}"
    )