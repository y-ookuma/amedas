# tool_AMeDAS

気象庁の過去の気象データ検索について、10分ごとの値ををスクレイピングした結果をデータフレームで返却します。CSV出力も可能です。


## 使用言語

- Python3

## 使用Pythonライブラリ
- pandas
- numpy
- tqdm

### Pythonライブラリ インストール方法

``` pip3 install pandas numpy tqdm ```


## AMeDASライブラリ
- ame_master.csv
  fuken_id,f_pre,f_tem,station_name,station_id のみ使用
※ [washitake.com](https://washitake.com/weather/amedas/obs_stations.md)より引用しています。


## 環境構築手順

- リポジトリをクローンします。  
  ```  git clone https://github.com/y-ookuma/amedas.git ```  
  もしくは  
  ```wget https://github.com/y-ookuma/amedas/archive/refs/heads/main.zip ```  
  ```unzip amedas-main.zip ```  


## 使用方法

- 2024-03-01〜2024-03-02 の「熊谷」,「さいたま」のアメダスのデータを取得します。
- station_id_list に 取得したい観測地点の station_id をセットします。station_idは ame_master.csv より確認ください。

```  
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

```

## Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
