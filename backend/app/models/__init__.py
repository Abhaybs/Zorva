# Models package — import all models so Base.metadata sees them.
from app.models.worker import Worker  # noqa: F401
from app.models.income import IncomeRecord  # noqa: F401
from app.models.gigscore import GigScoreRecord  # noqa: F401
from app.models.insurance import InsurancePolicy  # noqa: F401
from app.models.sos import SosEvent  # noqa: F401
