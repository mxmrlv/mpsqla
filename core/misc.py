from sqlalchemy import create_engine, orm


def create_resources(file_path):
    engine = create_engine('sqlite:////{path}'.format(path=file_path))
    session_factory = orm.sessionmaker(bind=engine)
    session = orm.scoped_session(session_factory=session_factory)
    return engine, session
