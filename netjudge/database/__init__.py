"""Database module initialisation."""
from netjudge.database.models import Base
from netjudge.database.common import engine

models.Base.metadata.create_all(engine)
