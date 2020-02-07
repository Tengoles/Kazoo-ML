from sqlalchemy import create_engine
import pandas as pd
from flaskr import model_settings

engine = create_engine(model_settings.engine_string)

query = """SELECT * FROM public."PCSEST" WHERE fechahora between '2019-10-18 11:30:03.655306' and '2019-10-18 11:33:03.655306' """
df = pd.read_sql(query, engine)