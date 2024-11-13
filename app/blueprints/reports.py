from flask import Blueprint, render_template
from app.db_connect import get_db
import pandas as pd
from app.functions import calculate_total_sales_by_region, analyze_monthly_sales_trends, get_top_performing_region

reports = Blueprint('reports', __name__)

@reports.route('/reports')
def show_reports():
    connection = get_db()
    query = """
        SELECT sd.sales_data_id, sd.monthly_amount, sd.date, r.region_name
        FROM sales_data sd
        JOIN regions r ON sd.region_id = r.region_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region_name'])

    # Ensure the date column is in datetime format for trend analysis
    df['date'] = pd.to_datetime(df['date'])

    # Perform analysis on the DataFrame (example: summary statistics)
    df_result = df.describe().reset_index()
    df_result.columns = ['sales_data_id', 'monthly_amount', 'region_name']
    analysis_result = df_result.to_html(classes='data-table table table-striped table-bordered', index=False, justify='center')

    # Perform analysis on the DataFrame (example: custom analysis)
    df_analysis = df.groupby('region_name')['monthly_amount'].sum().reset_index()
    df_analysis.columns = ['Region', 'Total Monthly Amount']
    analysis_table = df_analysis.to_html(classes='data-table table table-striped table-bordered', index=False, justify='center')

    # Use the analysis functions from functions.py
    total_sales_by_region = calculate_total_sales_by_region(df)
    monthly_sales_trend = analyze_monthly_sales_trends(df)
    top_performing_region = get_top_performing_region(total_sales_by_region)

    # Convert the DataFrames to HTML tables for display
    total_sales_html = total_sales_by_region.to_html(classes='data-table dataframe table table-striped table-bordered', index=False, justify='center')
    monthly_sales_trend_html = monthly_sales_trend.to_html(classes='data-table dataframe table table-striped table-bordered', index=False, justify='center')

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