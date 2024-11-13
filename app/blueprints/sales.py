from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd
import plotly.express as px
from app.functions import calculate_total_sales_by_region, analyze_monthly_sales_trends, get_top_performing_region

sales = Blueprint('sales', __name__)

# Route to display all sales data
@sales.route('/show_sales')
def show_sales():
    connection = get_db()
    query = """
        SELECT s.sales_data_id, s.monthly_amount, s.date, r.region_name
        FROM sales_data s
        JOIN regions r ON s.region_id = r.region_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region_name'])

    # Update the DataFrame to include Edit and Delete buttons
    df['Actions'] = df['sales_data_id'].apply(lambda l_id:
                                              f'<a href="{url_for("sales.edit_sales_data", sales_data_id=l_id)}" class="btn btn-sm btn-info">Edit</a> '
                                              f'<form action="{url_for("sales.delete_sales_data", sales_data_id=l_id)}" method="post" style="display:inline;">'
                                              f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
                                              )
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("sales_data.html", table=rows_only)


# Route to render the add sales data form
@sales.route('/add_sales_data', methods=['GET', 'POST'])
def add_sales_data():
    connection = get_db()
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region_id = request.form['region_id']  # Use numeric region_id

        query = "INSERT INTO sales_data (monthly_amount, date, region_id) VALUES (%s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (monthly_amount, date, region_id))
        connection.commit()
        flash("New sales data added successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    # Fetch regions for dropdown selection in the form
    with connection.cursor() as cursor:
        cursor.execute("SELECT region_id, region_name FROM regions")
        regions = cursor.fetchall()

    return render_template("add_sales_data.html", regions=regions)


# Route to handle updating a row
@sales.route('/edit_sales_data/<int:sales_data_id>', methods=['GET', 'POST'])
def edit_sales_data(sales_data_id):
    connection = get_db()
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region_id = request.form['region_id']

        query = "UPDATE sales_data SET monthly_amount = %s, date = %s, region_id = %s WHERE sales_data_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (monthly_amount, date, region_id, sales_data_id))
        connection.commit()
        flash("Sales data updated successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    query = """
        SELECT s.sales_data_id, s.monthly_amount, s.date, s.region_id, r.region_name
        FROM sales_data s
        JOIN regions r ON s.region_id = r.region_id
        WHERE s.sales_data_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (sales_data_id,))
        result = cursor.fetchone()

    # Fetch all regions for the dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT region_id, region_name FROM regions")
        regions = cursor.fetchall()

    return render_template("edit_sales_data.html", sales_data=result, regions=regions)


# Route to handle deleting a row
@sales.route('/delete_sales_data/<int:sales_data_id>', methods=['POST'])
def delete_sales_data(sales_data_id):
    connection = get_db()
    query = "DELETE FROM sales_data WHERE sales_data_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (sales_data_id,))
    connection.commit()
    flash("Sales data deleted successfully!", "success")
    return redirect(url_for('sales.show_sales'))

# Route to display all regions
@sales.route('/show_regions')
def show_regions():
    connection = get_db()
    query = "SELECT * FROM regions"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)
    # Update the Pandas DataFrame to include Edit and Delete buttons
    df['Actions'] = df['region_id'].apply(lambda r_id:
      f'<a href="{url_for("sales.edit_region", region_id=r_id)}" class="btn btn-sm btn-info">Edit</a> '
      f'<form action="{url_for("sales.delete_region", region_id=r_id)}" method="post" style="display:inline;">'
      f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
      )
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, header=False,
                            escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("regions.html", table=rows_only)

# Route to render the add region form
@sales.route('/add_region', methods=['GET', 'POST'])
def add_region():
    if request.method == 'POST':
        region_name = request.form['region_name']

        connection = get_db()
        query = "INSERT INTO regions (region_name) VALUES (%s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (region_name,))
        connection.commit()
        flash("New region added successfully!", "success")
        return redirect(url_for('sales.show_regions'))

    return render_template("add_region.html")

# Route to handle updating a region
@sales.route('/edit_region/<int:region_id>', methods=['GET', 'POST'])
def edit_region(region_id):
    connection = get_db()
    if request.method == 'POST':
        region_name = request.form['region_name']

        query = "UPDATE regions SET region_name = %s WHERE region_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (region_name, region_id))
        connection.commit()
        flash("Region updated successfully!", "success")
        return redirect(url_for('sales.show_regions'))

    query = "SELECT * FROM regions WHERE region_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (region_id,))
        result = cursor.fetchone()

    return render_template("edit_region.html", region=result)

# Route to handle deleting a region
@sales.route('/delete_region/<int:region_id>', methods=['POST'])
def delete_region(region_id):
    connection = get_db()

    # Check if the region is referenced in sales_data
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS Count FROM sales_data WHERE region_id = %s", (region_id,))
        count_result = cursor.fetchone()
        count = count_result['Count'] if count_result else 0

    if count > 0:
        flash("Cannot delete this region as it is referenced in sales data records.", "danger")
        return redirect(url_for('sales.show_regions'))

    # Proceed with deletion if no dependencies exist
    query = "DELETE FROM regions WHERE region_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (region_id,))
    connection.commit()
    flash("Region deleted successfully!", "success")
    return redirect(url_for('sales.show_regions'))

# Route to display reports
@sales.route('/reports')
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
    df_result = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount'])
    df_result = df_result.describe().reset_index()
    df_result.columns = ['Statistic', 'Value']
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

# Route to display visualizations
@sales.route('/show_visualization')
def show_visualization():
    # Connect to the database and fetch data
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

    # Use the analysis functions from functions.py
    total_sales_by_region = calculate_total_sales_by_region(df)
    monthly_sales_trend = analyze_monthly_sales_trends(df)
    top_performing_region = get_top_performing_region(total_sales_by_region)

    # Convert Period objects to strings for JSON serialization
    monthly_sales_trend['Month'] = monthly_sales_trend['Month'].astype(str)

    # Generate Plotly visualizations
    total_sales_fig = px.bar(total_sales_by_region, x='Region', y='Total Sales', title='Total Sales by Region')
    total_sales_plot = total_sales_fig.to_html(full_html=False)

    monthly_sales_fig = px.line(monthly_sales_trend, x='Month', y='Total Sales', title='Monthly Sales Trend')
    monthly_sales_plot = monthly_sales_fig.to_html(full_html=False)

    return render_template(
        "visualization.html",
        total_sales_plot=total_sales_plot,
        monthly_sales_plot=monthly_sales_plot)
