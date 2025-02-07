import os
import pandas as pd

# 対象の親ディレクトリを指定（この中のフォルダを探索する）
parent_dir = "result"  # ここを適宜変更

# 出力ファイル名
output_file = "merged_output.csv"

# 結果を保存するリスト
all_data = []

# 親ディレクトリ内のフォルダを走査
for folder_name in os.listdir(parent_dir):
    folder_path = os.path.join(parent_dir, folder_name)

    # フォルダでない場合はスキップ
    if not os.path.isdir(folder_path):
        continue

    # フォルダ内のCSVファイルを取得
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(folder_path, file_name)

            try:
                # CSVファイルを読み込む
                df = pd.read_csv(file_path, dtype=str)  # 文字列型で読み込む（郵便番号の0落ち対策）

                # 指定の3列が存在するか確認
                required_columns = ["事業所名称", "事業所郵便番号", "事業所所在地"]
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    print(f"警告: {file_path} には {missing_columns} の列がありません。スキップします。")
                    continue

                # 必要な列のみ取得
                extracted_df = df[required_columns]

                # データをリストに追加
                all_data.append(extracted_df)

            except Exception as e:
                print(f"エラー: {file_path} の処理中にエラーが発生しました: {e}")

# 全てのデータを結合
if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    # 結果をCSVファイルに保存（Excel対応のエンコーディングで出力）
    merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"処理が完了しました。結果は {output_file} に保存されました。")
else:
    print("処理対象のデータがありませんでした。")
