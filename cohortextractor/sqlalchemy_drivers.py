DRIVERS = {"mssql": "mssql+pymssql"}


def set_driver(engine_url):
    drivername = engine_url.drivername
    # By default we let SQLAlchemy pick the appropriate driver, this just
    # allows us to override it in specific cases
    new_drivername = DRIVERS.get(drivername, drivername)
    return engine_url.set(drivername=new_drivername)
