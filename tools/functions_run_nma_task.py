from celery import Celery
import os
import pandas as pd
from tools.utils import get_network_new, run_network_meta_analysis
import json

from dotenv import load_dotenv

load_dotenv()  # loads values from .env if not set

redis_url = os.environ['REDIS_URL']
celery_app = Celery('tasks', broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_backend=redis_url,
    broker_connection_retry_on_startup=True
)

@celery_app.task(bind=True)
def run_nma_task(self, net_data_json, num_outcome):
    try:
        net_data = pd.read_json(net_data_json, orient='split')
        results = []
        
        for i in range(int(num_outcome)):
            # Explicit state update
            self.update_state(
                state='STARTED',
                meta={
                    'current': i + 1,
                    'total': num_outcome,
                    'status': f'Processing outcome {i+1}/{num_outcome}'
                }
            )
            
            # Process data
            _ = get_network_new(df=net_data, i=i)
            nma_result = run_network_meta_analysis(net_data, i)
            results.append(nma_result.to_json(orient='split'))
        
        return {'status': 'SUCCESS', 'result': results}
    
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e)
            }
        )
        raise