import data_fetcher
import indicators
import report_generator
import os

def main():
    print("=== 山西焦煤投资追踪系统启动 ===")
    
    # 1. 抓取所有必要数据
    print("\n[1/3] 正在获取期货及手工基本面数据...")
    data = data_fetcher.fetch_all_data()
    
    if data is None:
        print("❌ 获取数据失败，流程终止。")
        return
        
    print(f"获取成功！当前期货日期: {data.get('jm_futures_date')}, 现货手工数据日期: {data.get('mysteel_date')}")

    # 2. 传入指标引擎计算评分与信号
    print("\n[2/3] 正在计算周期评分与反转信号...")
    analysis_result = indicators.analyze(data)
    
    print(f"当前得分: {analysis_result['cycle_score']}")
    print(f"当前状态: {analysis_result['cycle_status']}")
    
    # 3. 输出报告
    print("\n[3/3] 正在生成投资简报 Markdown 文件...")
    report_generator.generate_markdown_report(data, analysis_result)
    
    print("\n=== 运行结束 ===")

if __name__ == "__main__":
    main()
