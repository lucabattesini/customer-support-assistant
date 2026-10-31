from app.core.settings import get_settings
from app.db.sample_data import load_sample_data
from app.db.session import build_engine, build_session_factory, init_db, session_scope


def main() -> None:
    settings = get_settings()
    engine = build_engine(settings.resolved_database_url)
    init_db(engine)
    with session_scope(build_session_factory(engine)) as session:
        load_sample_data(session)
    print(f"Sample data loaded into {settings.resolved_database_url}")


if __name__ == "__main__":
    main()
