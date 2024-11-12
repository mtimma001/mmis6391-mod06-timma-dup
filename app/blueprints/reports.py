from flask import Blueprint, render_template
from app.db_connect import get_db
import pandas as pd
from app.functions import calculate_total_sales_by_region, analyze_monthly_sales_trends, get_top_performing_region

reports = Blueprint('reports', __name__)


@reports.route('/reports')
def show_reports():
    connection = get_db()
    query = "SELECT * FROM sales_data"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region'])

    # Ensure the date column is in datetime format for trend analysis
    df['date'] = pd.to_datetime(df['date'])

    # Perform analysis on the DataFrame (example: summary statistics)
    df_result = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region'])
    df_result = df_result.describe().reset_index()
    df_result.columns = ['Statistic', 'Value']
    analysis_result = df_result.to_html(classes='data-table table table-striped table-bordered', index=False,
                                        justify='center')

    # Perform analysis on the DataFrame (example: custom analysis)
    df_analysis = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region'])
    df_analysis = df_analysis.groupby('region')['monthly_amount'].sum().reset_index()
    df_analysis.columns = ['Region', 'Total Monthly Amount']
    analysis_table = df_analysis.to_html(classes='data-table table table-striped table-bordered', index=False,
                                         justify='center')
    #
    # # 1. Total Sales by Region
    # total_sales_by_region = df.groupby('region')['monthly_amount'].sum().reset_index()
    # total_sales_by_region.columns = ['Region', 'Total Sales']
    # total_sales_html = total_sales_by_region.to_html(classes='data-table dataframe table table-striped table-bordered',
    #                                                  index=False, justify='center')
    #
    # # 2. Monthly Sales Trend
    # df['month'] = df['date'].dt.to_period('M')  # Extract the month for trend analysis
    # monthly_sales_trend = df.groupby('month')['monthly_amount'].sum().reset_index()
    # monthly_sales_trend.columns = ['Month', 'Total Monthly Sales']
    # monthly_sales_trend_html = monthly_sales_trend.to_html(classes='data-table dataframe table table-striped table-bordered',
    #                                                        index=False, justify='center')
    #
    # # 3. Top-Performing Region
    # top_performing_region = total_sales_by_region.sort_values(by='Total Sales', ascending=False).iloc[0]
    # top_region_summary = f"The top-performing region is {top_performing_region['Region']} with total sales of ${top_performing_region['Total Sales']:.2f}."

    # Use the analysis functions from functions.py
    total_sales_by_region = calculate_total_sales_by_region(df)
    monthly_sales_trend = analyze_monthly_sales_trends(df)
    top_performing_region = get_top_performing_region(total_sales_by_region)

    # Convert the DataFrames to HTML tables for display
    total_sales_html = total_sales_by_region.to_html(classes='data-table dataframe table table-striped table-bordered',
                                                     index=False, justify='center')
    monthly_sales_trend_html = monthly_sales_trend.to_html(classes=' data-table dataframe table table-striped table-bordered',
                                                           index=False, justify='center')

    # Create a summary for the top-performing region
    top_region_summary = f"The top-performing region is {top_performing_region['Region']} with total sales of ${top_performing_region['Total Sales']:.2f}."


    return render_template(
    "reports.html",
           analysis_result=analysis_result,
           analysis_table=analysis_table,
           total_sales_table=total_sales_html,
           monthly_sales_table=monthly_sales_trend_html,
           top_region_summary=top_region_summary
    )
