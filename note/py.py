def test_set():
    data = {
        'name-test-1': {'data': True},
        'name-test-2': {'data': 1},
        'name-test-3': {'data': 123}
    }
    for key in list(data):
        data[key] = json.dumps(data[key], ensure_ascii=False)

    db = redis.Redis(connection_pool=redis_conn_pool)
    r = db.mset(data)
    print(r)
