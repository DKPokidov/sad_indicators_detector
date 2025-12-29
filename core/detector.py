import pandas as pd
import numpy as np
from utils.utils import DataUtils

class ZeroDetector:
    '''Класс для валидации показателей социально-экономического развития,
    представленных на Просторе'''

    def __init__(self, data_utils: DataUtils = None):
        self.data_utils = data_utils or DataUtils()

    def zero_detector(self, df: pd.DataFrame, territory_index: int, seeking_value: float, final_table: pd.DataFrame) -> pd.DataFrame:
        '''Основной метод для классификации обновлений
        0 - значение CЭР равно нулю
        1 - значение CЭР больше нуля
        None - значение СЭР отсутсвтует'''

        sir_indicators = pd.DataFrame(df['properties.indicators'][territory_index])
        name = df['properties.name'][territory_index]

        final_table[name] = None
        for idx, row in sir_indicators.iterrows():
            name_full_value = row['name_full'] 
            match_mask = (final_table['value_name'].str.replace(' ', '').str.strip().str.lower() ==
                name_full_value.replace(' ', '').strip().lower())

            if match_mask.any(): 
                if row['value'] == seeking_value:
                    final_table.loc[match_mask, name] = 0
                else:
                    final_table.loc[match_mask, name] = 1
        
        return final_table
    
    def change_func(self, value: float) -> int:
        '''Функция для замены абсолютных значений на:
            0 - значение CЭР равно нулю
            1 - значение CЭР больше нуля
            None - значение СЭР отсутсвтует
           '''
        if pd.isna(value):
            return value
        elif value > 0.0:
            return int(1)
        elif value == 0.0:
            return int(0)
        else:
            return None
        
    def region_sad_maker(self, df: pd.DataFrame) -> pd.DataFrame:
        '''Функция для создания таблицы СЭРов регионов по районом
            с абсолютными значениями показателей '''
        
        sad_list = []
        district_list = []
        for index, row in df.iterrows():
            district_list.append(row['properties.name'])
            indicators_df = pd.DataFrame(df['properties.indicators'][index])
            indicators = indicators_df['name_full'].to_list()
            if len(indicators) > len(sad_list):
                sad_list = indicators

        final_table = pd.DataFrame(index=sad_list, 
                            columns=df['properties.name'].to_list()).sort_index()

        for index in range(len(df)):
            sir_indicators = pd.DataFrame(df['properties.indicators'][index])
            sir_indicators = sir_indicators.sort_values(by='name_full', ascending=True)
            values = sir_indicators['value'].values
            district = district_list[index]
            if len(values) < len(final_table):
                values = np.concatenate([values, [None] * (len(final_table) - len(values))])
            elif len(values) > len(final_table):
                values = values[:len(final_table)]
            else:
                final_table[district] = values

        return final_table
    
    def zero_one_swinger(self, df: pd.DataFrame) -> pd.DataFrame:
        sad_table = self.region_sad_maker(df)
        return sad_table.apply(lambda col: col.apply(self.change_func))
        