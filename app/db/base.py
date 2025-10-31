# Import the Base class from the new file
from app.db.base_class import Base

# Import all the models, so that Base has them registered and Alembic can see them.
from app.models.user import User  # noqa
from app.models.item import Item  # noqa