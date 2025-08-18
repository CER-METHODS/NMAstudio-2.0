import dash
from dash import ctx, no_update
import dash_html_components as html
from tools.functions_run_nma_task import run_nma_task
from celery.result import AsyncResult
from tools.functions_run_nma_task import celery_app
from dash.exceptions import PreventUpdate
import redis

def __handle_nma_processing__(modal_open, n_intervals, num_outcome, net_data_storage, 
                         forest_data_storage, task_store_data):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "modal_data_checks":
        if not modal_open:
            return False, '', None, '', None, forest_data_storage, True
        
        try:
            # Start the async task
            task = run_nma_task.delay(net_data_storage[0], num_outcome)
            return (
                False,
                '',
                html.P("Starting network meta-analysis...", style={"color": "blue"}),
                '',
                {'task_id': task.id, 'status': ''},
                forest_data_storage,
                False  # Enable polling
            )
        except Exception as e:
            return True, str(e), None, '',None, forest_data_storage, True
    
    elif trigger_id == "nma-task-poller":
        if not task_store_data or 'task_id' not in task_store_data:
            raise PreventUpdate
            
        task_id = task_store_data['task_id']
        task = AsyncResult(task_id, app=celery_app)
        if task.state == 'PENDING':
            return (
                no_update,
                no_update,
                html.P("Task queued, waiting to start...", style={"color": "gray"}),
                no_update,
                no_update,
                no_update,
                False
            )
        
        elif task.state == 'STARTED':
            progress_info = task.info
            progress = progress_info.get('current', 0)
            total = progress_info.get('total', 1)
            
            return (
                no_update,
                no_update,
                html.Div([
                    html.P(f"Processing outcome {progress} of {total}"),
                ]),
                no_update,
                {'task_id': task_id, 'status': 'PROGRESS'},
                no_update,
                False
            )
        
        elif task.state == 'SUCCESS':
            return (
                False,
                '',
                html.Div([
                    html.P("✓ Analysis completed successfully!", 
                          style={"color": "green", "fontWeight": "bold"})
                ]),
                '__Para_Done__',
                {'task_id': task_id, 'status': 'COMPLETED'},
                task.result.get('result'),
                True
            )
        
        elif task.state == 'FAILURE':
            error_info = task.info
            error_msg = error_info.get('exc_message', 'Unknown error occurred')
            return (
                True,
                error_msg,
                html.Div([
                    html.P("❌ Analysis failed", 
                          style={"color": "red", "fontWeight": "bold"}),
                    html.P("Please check your data and try again.", 
                          style={"color": "gray", "fontSize": "0.9em"})
                ]),
                '',
                {'task_id': task_id, 'status': 'FAILED'},
                forest_data_storage,
                True
            )
    
    return no_update, no_update, no_update, no_update, no_update, no_update, True