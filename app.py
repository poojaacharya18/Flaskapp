import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)

            
            df['date'] = df['date'].astype(str)
            df['time'] = df['time'].astype(str)

           
            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], errors='coerce')

            
            df['time_diff'] = df['datetime'].diff().dt.total_seconds().fillna(0)

           
            df['inside_outside'] = df['position'].str.lower()

            
            duration_summary = df.groupby(['date', 'inside_outside'])['time_diff'].sum().reset_index()

            
            activity_summary = df.groupby(['date', 'activity']).size().reset_index(name='count')

            
            pick_activities = activity_summary[activity_summary['activity'] == 'picked'][['date', 'count']].rename(columns={'count': 'pick_activities'})
            place_activities = activity_summary[activity_summary['activity'] == 'placed'][['date', 'count']].rename(columns={'count': 'place_activities'})
            inside_duration = duration_summary[duration_summary['inside_outside'] == 'inside'][['date', 'time_diff']].rename(columns={'time_diff': 'inside_duration'})
            outside_duration = duration_summary[duration_summary['inside_outside'] == 'outside'][['date', 'time_diff']].rename(columns={'time_diff': 'outside_duration'})

           
            final_output = pd.merge(pick_activities, place_activities, on='date', how='outer')
            final_output = pd.merge(final_output, inside_duration, on='date', how='outer')
            final_output = pd.merge(final_output, outside_duration, on='date', how='outer')

            
            final_output.fillna(0, inplace=True)

            return render_template('result.html', tables=[final_output.to_html(classes='data')], titles=final_output.columns.values)

    return '''
    <h1>Upload Excel File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
