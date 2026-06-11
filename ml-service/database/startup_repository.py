from database.supabase_client import supabase


def create_startup(startup_data):

    return (
        supabase
        .table("startups")
        .insert(startup_data)
        .execute()
    )


def get_all_startups():

    return (
        supabase
        .table("startups")
        .select("*")
        .execute()
    )


def startup_exists(name):

    result = (
        supabase
        .table("startups")
        .select("id")
        .eq("name", name)
        .execute()
    )

    return len(result.data) > 0


def get_unenriched_startups(limit=20):

    return (
        supabase
        .table("startups")
        .select("*")
        .eq("enriched", False)
        .limit(limit)
        .execute()
    )


def update_startup(startup_id, data):

    return (
        supabase
        .table("startups")
        .update(data)
        .eq("id", startup_id)
        .execute()
    )