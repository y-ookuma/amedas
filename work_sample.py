from get_amedas import Amedas

start_day="2024-03-01"
end_day="2024-03-02"

amedas=Amedas(lib="ame_master.csv",start_day=start_day,end_day=end_day)
# station_id 熊谷,さいたま
station_id_list=[47626,363]
amedas.get_1by1(output_csv=True, station_id_list=station_id_list)
#amedas.get_bulk(output_csv=True)
