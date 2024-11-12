from flask import Blueprint, render_template
import plotly.express as px
import pandas as pd
from app.db_connect import get_db

visualization = Blueprint('visualization', __name__)


@visualization.route('/show_visualization')
def show_visualization():
    # Connect to the database and fetch data
    connection = get_db()
    query = "SELECT region, SUM(monthly_amount) as total_sales FROM sales_data GROUP BY region"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(result, columns=['region', 'total_sales'])

    # Create a bar chart using Plotly
    fig = px.bar(df, x='region', y='total_sales', title='Total Sales by Region',
                 labels={'total_sales': 'Total Sales', 'region': 'Region'})

    # Convert the plot to HTML and pass it to the template
    chart_html = fig.to_html(full_html=False)

    return render_template("visualization.html", chart_html=chart_html)
