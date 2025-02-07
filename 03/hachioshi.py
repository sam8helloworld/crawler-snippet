import pandas as pd

# 入力CSVファイル名
input_file = "result/八尾市＠障害福祉＆児童.xls/output.csv"  # 変更してください
output_file = "filtered_output.csv"  # 出力するCSVファイル名

# CSVファイルを読み込む
df = pd.read_csv(input_file)

# 抽出する対象の列リスト
target_columns = ["生活介護", "生活訓練", "機能訓練", "就移一般", "就継Ａ型", "就継Ｂ型"]

# 指定の6列のどれかに "○" がある行のみ抽出
filtered_df = df[df[target_columns].apply(lambda row: "○" in row.values, axis=1)]

# 「所在地」列の先頭に「大阪府八尾市」を付与
if "所在地" in filtered_df.columns:
    filtered_df["所在地"] = "大阪府八尾市" + filtered_df["所在地"].astype(str)

# 抽出後のデータをCSVとして保存（Excelで開きやすいよう utf-8-sig でエンコード）
filtered_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"処理が完了しました。結果は {output_file} に保存されました。")
