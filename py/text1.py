def Process(x):
    # 將字串依照空白切分
    parts = x.split(" ")
    # 取得第一部分並去掉 "我是"
    school = parts[0].replace("我是", "")
    # 取得第三部分 (姓名)
    name = parts[2]
    print(f"學校:{school}\n姓名:{name}")

# --- 關鍵改動：避免被 import 時執行 ---
if __name__ == "__main__":
    # 這裡放你原本的測試碼
    Name = "我是靜宜大學 資管二A 陳楷修"
    Process(Name)