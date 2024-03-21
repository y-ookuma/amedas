from tool_amedas import Amedas

start_day="2024-03-01"  #開始日を指定
end_day="2024-03-02"    #終了日を指定

amedas=Amedas(lib="ame_master.csv",start_day=start_day,end_day=end_day)

# 任意の観測地点を取得する
# station_id 熊谷,さいたま  ame_master.csvより観測地点のstation_idをセットしてください。
station_id_list=[47626,363]
amedas.get_data_per_10min_1by1(output_csv=True, station_id_list=station_id_list)

# 全観測地点を取得する場合、以下の関数を実行してください。
#amedas.get_data_per_10min_bulk(output_csv=True)
