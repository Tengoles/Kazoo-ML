from sqlalchemy import create_engine
import pandas as pd
from flaskr import model_settings

engine = create_engine(model_settings.engine_string)
tabla = "hubs_ml"
hubs = pd.DataFrame()
hubs["hub_name"] = ['PCSEST_E2_17', 'PCSEST_E2_CRUZADO', 'PCSEST_E1_MEDIO', 'PCSEST_E3_ENTRADA',
                    'PCSEST_E3_14', 'PCSEST_B1_21', 'PCSEST_B1_19', 'PCSEST_B1_20', 'PCSEST_B1_23',
                    'PCSEST_A1_8', 'PCSEST_A1_MEDIO', 'PCSEST_A1_9', 'PCSEST_C1_10', 'PCSEST_A2_1',
                    'PCSEST_C1_24', 'PCSEST_C1_11', 'PCSEST_C2_4', 'PCSEST_C2_6', 'PCSEST_A2_3',
                    'PCSEST_EURO_N1', 'PCSEST_EURO_N2']
hubs["ml_table"] = "PCSEST"
hubs.to_sql(tabla, engine, if_exists='append', index=False)