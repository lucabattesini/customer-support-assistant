import argparse

from app.core.settings import get_settings
from app.db.seed import is_empty, load_seed_data
from app.db.session import build_engine, build_session_factory, init_db, session_scope


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the store data into the database.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="replace existing data, including registered handoffs",
    )
    args = parser.parse_args()

    settings = get_settings()
    engine = build_engine(settings.database_url)
    init_db(engine)
    with session_scope(build_session_factory(engine)) as session:
        if not args.reset and not is_empty(session):
            print("Database already has data; use --reset to reload it")
            return
        load_seed_data(session, settings.seed_dir)
    print(f"Store data loaded into {settings.database_url}")


if __name__ == "__main__":
    main()
