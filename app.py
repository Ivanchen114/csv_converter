from flask import Flask, request, send_file, render_template
import pandas as pd
import io

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # 渲染 index.html 頁面

@app.route("/upload", methods=["POST"])
def upload():
    # 確保有收到檔案
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    # 讀取 CSV 檔案
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

if __name__ == "__main__":
    app.run(debug=True)
