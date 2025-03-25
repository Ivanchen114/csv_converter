from flask import Flask, request, send_file, render_template_string
import pandas as pd
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 取得上傳的 CSV 檔案
        file = request.files["file"]
        df = pd.read_csv(file, encoding="utf-8-sig")

        # 轉換時間格式（800 → 08:00）
        def format_time(time_str):
            try:
                time_str = str(int(time_str)).zfill(4)  # 確保是4位數
                return f"{time_str[:2]}:{time_str[2:]}"  # 轉換為 HH:MM
            except:
                return ""

        # 建立新的 DataFrame 以符合標準格式
        df_standard = pd.DataFrame({
            "Subject": df["活動名稱"],
            "Start Date": df["開始日期"],
            "Start Time": df["開始時間"].apply(format_time),
            "End Date": df["結束日期"],
            "End Time": df["結束時間"].apply(format_time),
            "All Day Event": df.apply(
                lambda row: "" if not ((pd.isna(row["開始時間"]) or row["開始時間"]=="00:00") and 
                                         (pd.isna(row["結束時間"]) or row["結束時間"]=="00:00"))
                           else "TRUE", axis=1),
            "Description": df["申請人"],  # 變更為申請人欄位
            "Location": df["場地"]
        })

        # 將轉換後的 CSV 檔案儲存在記憶體
        csv_buffer = io.StringIO()
        df_standard.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_buffer.seek(0)

        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode("utf-8-sig")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="standardized.csv"
        )

    return render_template_string("""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>CSV 格式轉換</title>
      </head>
      <body>
        <h1>CSV 格式轉換工具</h1>
        <form action="/" method="post" enctype="multipart/form-data">
          <label for="file">請選擇非標準格式 CSV 檔案：</label>
          <input type="file" name="file" id="file" accept=".csv">
          <br><br>
          <input type="submit" value="上傳並轉換">
        </form>
      </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
