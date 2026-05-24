from app import app
client = app.test_client()
payload = {
    'subjects': ['python', 'data science'],
    'timeline': 28,
    'daily_hours': 1,
    'goals': 'Learn basics and build small projects',
    'difficulty_level': 'beginner',
    'learning_style': 'visual'
}
resp = client.post('/api/study-plan', json=payload)
print('status', resp.status_code)
print(resp.get_json().get('plan', {}).get('metadata', {}))
print('days', len(resp.get_json().get('plan', {}).get('daily_breakdown', [])))
