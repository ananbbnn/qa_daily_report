from flask import Flask, render_template, request
import pandas as pd
import os
import json
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_stats():
    if os.path.exists(UPLOAD_FOLDER):
        with open(UPLOAD_FOLDER, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(UPLOAD_FOLDER, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    filename = None
    report_date = ''

    if request.method == 'POST':
        file = request.files['file']
        report_date = request.form['report_date'].replace('-', '')
        if file and file.filename.endswith('.csv'):
            # 儲存檔案
            today_str = datetime.now().strftime('%Y%m%d')
            filename = f"{UPLOAD_FOLDER}/qa_{report_date}.csv"
            file.save(filename)

            # 讀檔與處理
            df = pd.read_csv(filename)
            df['回報日期'] = pd.to_datetime(df['回報日期'], errors='coerce')
            df['已更新'] = pd.to_datetime(df['已更新'], errors='coerce')
            if report_date== today_str:
                today = pd.to_datetime('today').normalize()
            else:
                today = pd.to_datetime(report_date, format='%Y%m%d')
            df = df.fillna('')
            # 各種統計
            fixed_keys = ['ema.hong', 'Szi', 'weiren.yang', 'yuwei.dee', 
              'frank.huang', 'jiaying.cai', 'robin.wen', 
              'david.chen', 'jian.du']
            people_results = {person: {} for person in fixed_keys}

            # 新問題
            new_issues = df[(df['狀態'] == '已分配') & (df['回報日期'] == today)]['分配給'].value_counts().to_dict()
            # 今日完成
            done_tested = df[(df['狀態'] == '已測試') & (df['已更新'] == today)]
            done_tested_count = done_tested['回報人'].value_counts().to_dict()
            done_assigned = df[(df['狀態'] == '待測試') & (df['已更新'] == today)]
            done_assigned_count = done_assigned['分配給'].value_counts().to_dict()
            combined_done = {**done_tested_count, **done_assigned_count}
            # 累積未完成
            cumulative_unfinished = df[df['狀態'] == '已分配']['分配給'].value_counts().to_dict()
            # 重要未處理
            important_unprocessed = df[(df['狀態'] == '已分配') & (df['嚴重性'] == '重要')]['分配給'].value_counts().to_dict()
            # 外部未處理
            external_unprocessed = df[(df['狀態'] == '已分配') & (df['類別'] == 'HAPCS疾管署_愛滋追管系統')]['分配給'].value_counts().to_dict()
            
            daily_results = {
                '新問題': new_issues,
                '今日完成': combined_done,
                '累積未完成': cumulative_unfinished,
                '重要未處理': important_unprocessed,
                '外部未處理': external_unprocessed
            }
            # 統計分類
            all_categories = list(daily_results.keys())
            # 寫入統計
            for cat, data in daily_results.items():
                for person, count in data.items():
                    if person in people_results:
                        people_results[person][cat] = count
            # 合計
            people_results['合計'] = {}
            total_count = [sum(i.values()) for i in daily_results.values()]
            for i,key in  enumerate(daily_results.keys()):
                people_results['合計'][key] = total_count[i]






            print(f'print:{people_results}')
            
           
            
            

    return render_template('index.html', results=results, filename=filename  ,report_date=report_date)

if __name__ == '__main__':
    app.run(debug=True)




'''
            form_title = ['ema.hong',
                        'Szi',
                        'weiren.yang',
                        'yuwei.dee',
                        'frank.huang',
                        'jiaying.cai',
                        'robin.wen',
                        'david.chen',
                        'jian.du',
                        '合計',
                        '待測試']
            # 新問題
            new_issues = df[(df['狀態'] == '已分配') & (df['回報日期'] == today)]['分配給'].value_counts().to_dict()
            # 今日完成
            done_tested = df[(df['狀態'] == '已測試') & (df['已更新'] == today)]
            done_tested_count = done_tested['回報人'].value_counts().to_dict()
            done_assigned = df[(df['狀態'] == '待測試') & (df['已更新'] == today)]
            done_assigned_count = done_assigned['分配給'].value_counts().to_dict()
            combined_done = {**done_tested_count, **done_assigned_count}
            # 累積未完成
            cumulative_unfinished = df[df['狀態'] == '已分配']['分配給'].value_counts().to_dict()
            # 重要未處理
            important_unprocessed = df[(df['狀態'] == '已分配') & (df['嚴重性'] == '重要')]['分配給'].value_counts().to_dict()
            # 外部未處理
            external_unprocessed = df[(df['狀態'] == '已分配') & (df['類別'] == 'HAPCS疾管署_愛滋追管系統')]['分配給'].value_counts().to_dict()
            # 待測試
            under_test = df['狀態'] == '待測試'
            under_test = under_test.sum()
            # 統計結果
            daily_results = {
                '新問題': new_issues,
                '今日完成': combined_done,
                '累積未完成': cumulative_unfinished,
                '重要未處理': important_unprocessed,
                '外部未處理': external_unprocessed
            }
            results_total = [sum(i.values()) for i in daily_results.values()]
            results = daily_results
            # results['合計'] = results_total
            # results['待測試'] = under_test
            # 儲存統計
'''