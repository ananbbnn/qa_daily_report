#import os
#os.system('pip uninstall pandas -y && pip install pandas')
from sqlalchemy import create_engine ,text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import asyncio
from datetime import datetime




async def insert_data(row):
    data = str(tuple(row.tolist()))
    sql = """INSERT INTO `qa`
    (`id`,
    `project`,
    `reporter`,
    `receiver`,
    `priority`,
    `serverity`,
    `frequency`,
    `version`,
    `category`,
    `report_date`,
    `os`,
    `os_version`,
    `platform_category`,
    `public`,
    `update_date`,
    `status`,
    `analysys`,
    `fixed_version`)
    VALUES {}
    """.format(data).replace('nan','NULL')
    




    DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3306/qa"
    mysql_engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=mysql_engine)
    session = Session()
    session.execute(text(sql))
    session.commit()



async def main():
    today_str = f'{datetime.now().strftime('%Y%m%d')}.csv'
    try:
        df = pd.read_csv(r"C:\Users\ananb\OneDrive\Desktop\vs_code\qa_daily_report\uploads\qa_"+today_str)
    except:
        print(f'qa_{today_str} 此檔案不存在') 
        return  
    df = df.drop(columns= "摘要") 
    rows = df.values
    #for row in rows:
    #    insert_data(row)
    tasks = [insert_data(row) for row in rows]
    results = await asyncio.gather(*tasks)
    return

asyncio.run(main())
