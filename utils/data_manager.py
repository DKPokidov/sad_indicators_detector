import sys
sys.path.append(r'D:/Work/ITMO/AD/Prostor/Validation/module')

import os
import pandas as pd
from config.settings import in_path, out_file, region_tables, seeking_value

class DataUtils:
    '''Класс для загрузки и сохраниния данных'''

    @staticmethod
    def file_reader(excel: str) -> pd.DataFrame:
        '''Метод для чтения файлов'''
        path = f'{in_path}/{excel}'
        try:
            df = pd.read_json(path)
            sad_df = pd.json_normalize(df['features'])
            return sad_df
        except FileNotFoundError:
            print('Файл не найден!')
            return pd.DataFrame()
    
    @staticmethod    
    def demand_adder(df: pd.DataFrame) -> set:
        '''Метод для добавления строк с обеспеченностями к таблице со списком СЭР'''
        sir_indicators = pd.DataFrame(df['properties.indicators'][seeking_value])
        demand_df = sir_indicators.loc[
            sir_indicators['name_full'].str.contains('Обеспеченность', na=False)
        ]
        demand_set = set()
        for index in range(len(demand_df)):
            demand_set.add(demand_df['name_full'].iloc[index])
        return demand_set
    
    @staticmethod
    def write_to_new_sheets(region_list: list, df: pd.DataFrame):
        """Записывает данные в новые листы Excel-файла для каждого региона."""
        with pd.ExcelWriter(out_file, engine='openpyxl', mode='a' if os.path.exists(out_file) else 'w') as writer:
            for region in region_list:
                if region in writer.book.sheetnames:
                    print(f"Лист '{region}' уже существует, пропускаем")
                    continue
                
                df.to_excel(writer, sheet_name=region, index=False)
                print(f"Записан регион '{region}' в новый лист")
    
    @staticmethod
    def old_file_remove():
        '''Удаляем старый выходной файл, если он существует'''
        if os.path.exists(out_file):
            os.remove(out_file)

    @staticmethod
    def file_existing(region_list):
        '''проверка на наличие файлов для обработки'''
        if not region_list:
            print("ОШИБКА: Не найдено файлов для обработки")
            exit()
        else:
            print("Файлы для обработки найдены")
            
    @staticmethod
    def region_list_maker() -> list:
        '''Создает список регионов из имен файлов'''
        region_list = []
        for file in os.listdir(in_path):
            if file.endswith('.json') and file.startswith('indicator_values_'):
                region_name = file.replace('indicator_values_', '').replace('.json', '')
                region_list.append(region_name)
        print(f"Cоздан список регионов ({len(region_list)}):")
        for i, region in enumerate(sorted(region_list)):
            print(f"  {i+1}. '{region}'")
        return region_list
    
    @staticmethod
    def table_to_file(region_list: list):
        '''Записываем таблицы регионов в файл'''
        if region_tables:
            with pd.ExcelWriter(out_file, engine='openpyxl') as writer:
                for region in region_list:
                    if region in region_tables:
                        region_tables[region].to_excel(writer, sheet_name=region[:31], index=False)
                        print(f"Записан регион '{region}' в новый лист")
                    else:
                        print(f"Данные для региона '{region}' не найдены!")
                        # Создаем пустую таблицу для отсутствующего региона
                        pd.DataFrame(columns=['Data_type', 'value_name']).to_excel(
                            writer, 
                            sheet_name=region[:31], 
                            index=False
                        )
                        print(f"Создан пустой лист для региона '{region}'")

            print(f"\nВсе данные записаны в {out_file}")
        else:
            print('ОШИБКА: region_tables пустой!')
    