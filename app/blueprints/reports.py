from flask import Blueprint, render_template
from app.db_connect import get_db
import pandas as pd

reports = Blueprint('reports', __name__)


@reports.route('/reports')
def show_reports():
    connection = get_db()
    query = "SELECT * FROM sales_data"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Perform analysis on the DataFrame (example: summary statistics)
    df_result = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region'])
    df_result = df_result.describe().reset_index()
    df_result.columns = ['Statistic', 'Value']
    analysis_result = df_result.to_html(classes='data-table table table-striped table-bordered', index=False, justify='center')

    # Perform analysis on the DataFrame (example: custom analysis)
    df_analysis = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region'])
    df_analysis = df_analysis.groupby('region')['monthly_amount'].sum().reset_index()
    df_analysis.columns = ['Region', 'Total Monthly Amount']
    analysis_table  = df_analysis.to_html(classes='data-table table table-striped table-bordered', index=False, justify='center')

    return render_template("reports.html", analysis_result=analysis_result, analysis_table=analysis_table)