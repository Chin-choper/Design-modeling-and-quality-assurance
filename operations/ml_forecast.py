import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from django.conf import settings

matplotlib.use('Agg')

def create_forecast_graph():
    xlsx_folder = os.path.join(settings.BASE_DIR, 'main_xlsx')
    static_img_dir = os.path.join(settings.BASE_DIR, 'static', 'images')

    if not os.path.exists(static_img_dir):
        os.makedirs(static_img_dir)

    output_filename = 'forecast_chart.png'
    full_output_path = os.path.join(static_img_dir, output_filename)

    if os.path.exists(full_output_path):
        return output_filename
    data_list = []

    if not os.path.exists(xlsx_folder):
        print("Папка main_xlsx не знайдена")
        return None

    for filename in os.listdir(xlsx_folder):
        if filename.startswith('main_operations_') and filename.endswith('.xlsx'):
            try:
                parts = filename.split('_')
                year = parts[2]
                month = parts[3].split('.')[0]

                date_obj = pd.to_datetime(f"{year}-{month}-01")

                file_path = os.path.join(xlsx_folder, filename)
                df = pd.read_excel(file_path)

                total_exp = df['Експорт, USD'].sum()
                total_imp = df['Імпорт, USD'].sum()

                data_list.append({
                    'Date': date_obj,
                    'Export': total_exp,
                    'Import': total_imp
                })
            except Exception as e:
                print(f"Помилка {filename}: {e}")

    if not data_list:
        return None

    df_agg = pd.DataFrame(data_list).sort_values('Date')

    df_agg['Time_Index'] = np.arange(len(df_agg))

    X = df_agg[['Time_Index']]
    y_exp = df_agg['Export']
    y_imp = df_agg['Import']

    model_exp = LinearRegression().fit(X, y_exp)
    model_imp = LinearRegression().fit(X, y_imp)

    last_idx = df_agg['Time_Index'].max()
    future_indexes = np.arange(last_idx + 1, last_idx + 6).reshape(-1, 1)

    last_date = df_agg['Date'].iloc[-1]
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=5, freq='MS')

    pred_exp = model_exp.predict(future_indexes)
    pred_imp = model_imp.predict(future_indexes)

    plt.figure(figsize=(10, 6))

    plt.plot(df_agg['Date'], df_agg['Export'], label='Експорт (факт)', marker='o')
    plt.plot(df_agg['Date'], df_agg['Import'], label='Імпорт (факт)', marker='o')

    plt.plot(future_dates, pred_exp, label='Експорт (прогноз)', linestyle='--', marker='x', color='tab:blue')
    plt.plot(future_dates, pred_imp, label='Імпорт (прогноз)', linestyle='--', marker='x', color='tab:orange')

    plt.title('Прогноз імпорту та експорту')
    plt.xlabel('Дата')
    plt.ylabel('USD')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(full_output_path)
    plt.close()

    return output_filename
