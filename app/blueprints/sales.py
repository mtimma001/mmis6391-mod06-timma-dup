from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

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
