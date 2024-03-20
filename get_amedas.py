import requests,math,json,gc,sys,configparser,os
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta


def getJMA_Data_per_10min(url_p):

  def direction_to_angle(direction):
    if pd.isnull(direction):
        return np.nan
    directions = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東", "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西"]
    return directions.index(direction) * 22.5

  def angle_to_direction(angle):
    if pd.isnull(direction):
        return np.nan
    directions = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東", "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西"]
    return directions[int(round(angle / 22.5)) % 16]


  if int(url_p["station_id"]) <= 1000:
    url_p["station_id"] = str(url_p["station_id"]).zfill(4)

  # 並べ替えたい列の順序を指定します
  col_order = ['time_jst', 'air_pressure_land', 'air_pressure_sea', 'rainfall',
                 'temp', 'hum', 'wind_speed', 'wind_direct', 'wind_direct_degrees',
                 'max_gust_wind_speed', 'max_gust_wind_direct',
                 'max_gust_wind_direct_degrees','sunlight_hour']

  base_urls = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no={fuken_id}&block_no={station_id}&year={year}&month={month_str}&day={day_str}&view="
  base_urla = "https://www.data.jma.go.jp/obd/stats/etrn/view/10min_a1.php?prec_no={fuken_id}&block_no={station_id}&year={year}&month={month_str}&day={day_str}&view="


  # Dataframe 作成
  try:
    url = base_urls.format(**url_p) 
#    print(url)
    df = pd.read_html(url)[0]
  except:
    url = base_urla.format(**url_p) 
#    print(url)
    df = pd.read_html(url)[0]


  # カラムを取得
  rows, cols = df.shape   # 行数と列数を取得

  col=[]
  if cols==11:
    col=['hour_time','air_pressure_land', 'air_pressure_sea', 'rainfall',
               'temp', 'hum', 'wind_speed', 'wind_direct',
               'max_gust_wind_speed', 'max_gust_wind_direct','sunlight_hour']
  if cols==9:
    col=['hour_time', 'rainfall','temp', 'hum', 'wind_speed', 'wind_direct',
               'max_gust_wind_speed', 'max_gust_wind_direct','sunlight_hour']

  df.columns=col

  # "--"をnull（ここではnumpyのnan）に置き換え
  df = df.replace('静穏', '--')
  df = df.replace('×', '--')
  df = df.replace('///', '--')
  df = df.replace('\)', '', regex=True)
  df = df.replace('\]', '', regex=True)
  df = df.replace(' ', '', regex=True)
  df.replace('静穏', np.nan, inplace=True)
  df.replace('--', np.nan, inplace=True)

  # 時間修正 気象庁の"時分"は10分遅れの表記となるためtimeserise化するために修正
  time_series = pd.date_range(start='00:00', end='23:59', freq='10min')
  df['time'] = time_series[:len(df)] # Dfの行数と時系列データの長さを一致させる

  # 'time'列の時刻と年、月、日を結合
  df['time'] = df['time'].apply(lambda t: pd.Timestamp(year=url_p['year'], month=url_p['month'], day=url_p['day'], hour=t.hour, minute=t.minute))
 # 'time'列の時刻をJSTにローカライズ
  df['time_jst'] = df['time'].dt.tz_localize('Asia/Tokyo')
  # 'time'列の時刻をUTCに
  df['time'] = df['time_jst'].dt.tz_convert('UTC') #
  df.set_index('time', inplace=True) # index化
#  print(df.columns)
  df = df.drop('hour_time', axis=1)

  # 風向 360℃変換
  df["wind_direct_degrees"] = df["wind_direct"].apply(direction_to_angle)
#  df["wind_direct_rad"] = np.radians(df['wind_direct_degrees'])
  df["max_gust_wind_direct_degrees"] = df["max_gust_wind_direct"].apply(direction_to_angle)
#  df["max_gust_wind_direct_rad"] = np.radians(df['max_gust_wind_direct_degrees'])

  # カラムの順番を入れ替え
  # DataFrameに存在する列だけを取得します
  existing_columns = [col for col in col_order if col in df.columns]
  # 並べ替えたい列とそれ以外の列を結合します
  new_order = existing_columns + df.columns.drop(existing_columns).tolist()
  # 列を新しい順序に並べ替えます
  df = df[new_order]

  return df

class Amedas():
  # 設定ファイルを読み込む。
  def __init__(self, day_series=None, config=None, lib_df=None
                , lib=None, start_day=None, end_day=None):

    lib_filepath = os.path.dirname(os.path.abspath(__file__)) + '/' + lib
    lib_df = pd.read_csv(lib_filepath, encoding='utf-8')
    # station_idがnullでなく、f_temがYである行だけを保持します
    self.lib_df = lib_df[lib_df['station_id'].notna() & (lib_df['f_tem'] == 'Y')]

    # 現在の日付と時刻を取得
    now = datetime.now()
    # 昨日の日付を取得
    yesterday = now - timedelta(days=1)

    # start_day
    start_date = yesterday.date()
    if start_day != "":
      start_date = datetime.strptime(start_day, "%Y-%m-%d")

    # end_day
    end_date = yesterday.date()
    if end_day != "":
      end_date = datetime.strptime(end_day, "%Y-%m-%d")

    self.day_series = pd.date_range(start=start_date, end=end_date, freq='D')


  # bulk処理の場合
  def get_bulk(self,output_csv=bool):
    # 総行数を取得します
    rows = len(self.lib_df)
    icnt = 0
    for index,row in tqdm(self.lib_df.iterrows(), ncols=None):
      icnt += 1
      print("【%s/%s】 %s" % (str(icnt),rows,row["station_name"]))
      url_p={}
      url_p["fuken_id"]     = row["fuken_id"]
      url_p["type_"]        = row["type"]
      url_p["station_name"] = row["station_name"]
      url_p["f_tem"]        = row["f_tem"] #気温
      url_p["station_id"]   = int(row["station_id"])

      # 空のデータフレームを作成
      sum_df = pd.DataFrame()
      for date in self.day_series:
        url_p["year"] = date.year
        url_p["month"] = date.month
        url_p["day"] = date.day
        url_p["month_str"] = f"{date.month:02d}" # 月を2桁の文字列に変換
        url_p["day_str"] = f"{date.day:02d}"     # 日を2桁の文字列に変換

        df=getJMA_Data_per_10min(url_p)

        # データフレームを追加
        sum_df = pd.concat([sum_df, df])

    # CSVファイルに出力
    if output_csv:
      outputfile="/out/" + url_p["station_name"] + ".csv"
      filepath = os.path.dirname(os.path.abspath(__file__))+ outputfile
      sum_df.to_csv(filepath, index=True)
    return sum_df

  # 個別処理の場合
  def get_1by1(self,output_csv=bool,station_id_list=None):
    # セクションを指定してすべてのキーを取得
    icnt=0
    keys = station_id_list
    for k in tqdm(station_id_list, ncols=None):
      icnt+=1
      # station_idが指定の値である行を取得します。
      row = self.lib_df[self.lib_df['station_id'] == int(k)]
      # データフレームを辞書に変換します。
      dict_row = row.to_dict('records')

      print("【%s/%s】 %s" % (str(icnt),str(len(keys)-1),row["station_name"]))

      url_p={}
      url_p["fuken_id"]     = dict_row[0]["fuken_id"]
      url_p["type_"]        = dict_row[0]["type"]
      url_p["station_name"] = dict_row[0]["station_name"]
      url_p["f_tem"]        = dict_row[0]["f_tem"] #気温
      url_p["station_id"]   = int(dict_row[0]["station_id"])

      # 空のデータフレームを作成
      sum_df = pd.DataFrame()
      for date in self.day_series:
        url_p["year"] = date.year
        url_p["month"] = date.month
        url_p["day"] = date.day
        url_p["month_str"] = f"{date.month:02d}" # 月を2桁の文字列に変換
        url_p["day_str"] = f"{date.day:02d}"     # 日を2桁の文字列に変換

        df=getJMA_Data_per_10min(url_p)

        # データフレームを追加
        sum_df = pd.concat([sum_df, df])
        # CSVファイルに出力
      if output_csv:
        outputfile="/out/" + url_p["station_name"] + ".csv"
        filepath = os.path.dirname(os.path.abspath(__file__))+ outputfile
        sum_df.to_csv(filepath, index=True)
      return sum_df

