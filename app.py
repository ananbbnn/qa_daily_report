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
    people_results = {}
    all_categories = {}
    filename = None
    report_date = ''

    if request.method == 'POST':
        action = request.form.get('action')
        report_date = request.form['report_date'].replace('-', '')
        today_str = datetime.now().strftime('%Y%m%d')
        if action == 'upload':    #上傳按鍵
            file = request.files['file']
            if file and file.filename.endswith('.csv'):
                # 儲存檔案
                filename = f"{UPLOAD_FOLDER}/qa_{report_date}.csv"
                file.save(filename)

        elif action == 'query' and os.path.exists(f"{UPLOAD_FOLDER}/qa_{report_date}.csv"):    #查詢按鍵
            filename = f"{UPLOAD_FOLDER}/qa_{report_date}.csv"
        else:
            return render_template('index.html', 
                                   error=f'{report_date} 沒有紀錄。')

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
        # 補零
        for person in fixed_keys:
            for cat in all_categories:
                people_results[person][cat] = 0
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
        # 待測試
        under_test = df['狀態'] == '待測試'
        under_test = int(under_test.sum())
        people_results['待測試'] = {'新問題':under_test}

        
        if action == 'upload':
            print(f'print:{people_results}')
            # 儲存每月JSON檔
            month_key = report_date[:6]
            json_path = f"{UPLOAD_FOLDER}/JSON/qa_{month_key}.json"
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    monthly_data = json.load(f)
            else:
                monthly_data = {}
            monthly_data[report_date] = people_results
            sorted_data = dict(sorted(monthly_data.items()))    # 日期排序
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(sorted_data, f, ensure_ascii=False, indent=2)
            
            
    return render_template('index.html', 
                           results=people_results, 
                           filename=filename,
                           report_date=report_date, 
                           all_categories=all_categories)

@app.route('/month-trend', methods=['GET', 'POST'])
def monthtrend():
    monthly_data = {}
    result = {}
    if request.method == 'POST':
    # 重組資料
        month = request.form['monthSelector'].replace('-', '')
        json_path = f"{UPLOAD_FOLDER}/JSON/qa_{month}.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                monthly_data = json.load(f)
        else:
            return render_template('month-trend.html', error=f'{month} 沒有紀錄。')
        # 每一天的資料
        for date, daily_data in monthly_data.items():
            for person, metrics in daily_data.items():
                if person not in result:
                    # 初始化這個人
                    result[person] = {
                        'dates': [],
                        '新問題': [],
                        '今日完成': [],
                        '累積未完成': [],
                        '重要未處理': [],
                        '外部未處理': []
                    }
                # 寫入資料
                result[person]['dates'].append(date)
                for key in ['新問題', '今日完成', '累積未完成', '重要未處理', '外部未處理']:
                    result[person][key].append(metrics.get(key, 0))
        
        
    return render_template('month-trend.html', monthly_data=monthly_data, result=result)

if __name__ == '__main__':
    app.run(debug=True)
