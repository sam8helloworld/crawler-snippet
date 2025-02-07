import pandas as pd

# CSVファイルの読み込み
input_file = "result/枚方市指定障がい福祉サービス.xls/output.csv"  # 読み込むCSVファイルのパス
output_file = "output.csv"  # 出力するCSVファイルのパス

# CSVをDataFrameとして読み込む
df = pd.read_csv(input_file)

# 「事業所所在地」列の先頭に「大阪府」を付与
df["事業所所在地"] = "大阪府枚方市" + df["事業所所在地"].astype(str)

# 加工後のデータを新しいCSVとして出力
df.to_csv(output_file, index=False, encoding="utf-8-sig")  # utf-8-sig でExcel対応

print("変換が完了しました！")