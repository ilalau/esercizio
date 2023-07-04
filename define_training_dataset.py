import pandas as pd

def prepare_training_dataset(start_time, end_time):
    # Load the cooking metrics dataset
   # Load the datasets
    cooking_metrics = pd.read_csv('cooking_metrics.csv', delimiter=";", engine='python')
    batch_registry = pd.read_csv('batch_registry.csv', delimiter=";", engine='python')
    faulty_intervals = pd.read_csv('faulty_intervals.csv', delimiter=";", engine='python')

    # Filter data for machine m1 
    filtered_cooking_metrics = cooking_metrics[
        (cooking_metrics['machine_id'] == 'm1')
    ]

    # Filter data based on the specified time interval 
    filtered_cooking_metrics = filtered_cooking_metrics[
        (filtered_cooking_metrics['timestamp'] >= start_time) &
        (filtered_cooking_metrics['timestamp'] <= end_time)
    ]
    
    faulty_intervals = faulty_intervals[faulty_intervals['machine_id'] == 'm1']
    batch_registry = batch_registry[batch_registry['arepa_type'] == 'a1']

    # Remove faulty intervals that can be found in the corrispective csv
    for _, row in faulty_intervals.iterrows():
        faulty_start = row['start_time']
        faulty_end = row['end_time']
        filtered_cooking_metrics = filtered_cooking_metrics[
            ~((filtered_cooking_metrics['timestamp'] >= faulty_start) &
              (filtered_cooking_metrics['timestamp'] <= faulty_end))
        ]

    # Calculate hourly averaged metrics
    filtered_cooking_metrics['timestamp'] = pd.to_datetime(filtered_cooking_metrics['timestamp'])
    #hour_intervals = pd.date_range(start=start_date, end=end_date, freq='H')
    #hourly_averaged_metrics = filtered_cooking_metrics.resample('1H', on='timestamp').mean().reset_index()

    # Merge with batch registry to include batch information based on shared key
    training_dataset = pd.merge(filtered_cooking_metrics, batch_registry, on=['batch_id'])
    training_dataset['metric_1'] =  training_dataset['metric_1'].str.replace(',', '.').astype(float)
    training_dataset['metric_2'] =  training_dataset['metric_2'].str.replace(',', '.').astype(float)

    # Calculate the average between two metric values for the timestamp
    training_dataset['Average'] = (training_dataset['metric_1'] + training_dataset['metric_2']) / 2
    
    training_dataset.drop(['batch_id', 'metric_1','metric_2'], axis=1,inplace=True)
    
    return training_dataset