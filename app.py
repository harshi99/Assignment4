from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import matplotlib.pyplot as plt
import pyodbc
import io
import base64

# Blob Storage configuration
blob_connection_string = 'DefaultEndpointsProtocol=https;AccountName=assdata1;AccountKey=WMGVFc5Btn/cWP1ErRdsoFKp+VOWcfM9r5C6uOYSod9jeunIxoThQp+A6ecG6R48CFywsaCRl/AZ+ASttwd/CA==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
container_name = 'as'

# SQL configuration
server = 'harshi1.database.windows.net'
database = 'assdata2'
username = 'harshi'
password = 'Azure.123'
driver = '{ODBC Driver 18 for SQL Server};Server=tcp:harshi1.database.windows.net,1433;Database=assdata2;Uid=harshi;Pwd=Azure.123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

# Establish the database connection
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
connection = pyodbc.connect(connection_string)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        # Execute the query and retrieve data from the database
        data = execute_query(query)
        # Generate the chart
        chart_type, chart_url = generate_chart(data)
        return render_template('index.html', chart_type=chart_type, chart_url=chart_url)
    return render_template('index.html')

def generate_chart(data, bar_width=20, bar_height=6):
    # Perform necessary data processing
    values = [item[0] for item in data]
    unique_values = list(set(values))
    value_counts = [values.count(value) for value in unique_values]

    # Generate a pie chart or bar graph using Matplotlib
    fig, ax = plt.subplots(figsize=(bar_width, bar_height))
    if len(unique_values) <= 10:
        # Pie chart for fewer unique values
        ax.pie(value_counts, labels=unique_values, autopct='%1.1f%%')
        chart_type = 'pie'
    else:
        # Bar graph for more unique values
        x = range(len(unique_values))
        ax.bar(x, value_counts)
        ax.set_xticks(x)
        ax.set_xticklabels(unique_values)
        chart_type = 'bar'

    # Convert the chart to an image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    plt.close(fig)  # Close the figure to release resources

    # Return the chart type and the rendered template with the chart
    return chart_type, chart_url

def execute_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return data

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(debug=True)
    app.run(host='localhost', port=port)
    
