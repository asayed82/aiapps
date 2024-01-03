from main import create_app

def test_hello():
    app = create_app()
    client = app.test_client()

    res = client.post("/", json={"var1": "hello", "var2": "world"})

    print(res)


def test_create_table():
    app = create_app()
    client = app.test_client()

    res = client.post("/create_table")

    print(res)


def test_process_local_docs():
    app = create_app()
    client = app.test_client()

    res = client.post(
        "/process_local_docs",
        json={
            "local_dir_path": "/Users/ahmadelsayed/Desktop/dev/master-demos/apps/docprocess/data/data_html",
            "file_type": "HTML",
        },
    )

    print(res)


def test_process_remote_docs():
    app = create_app()
    client = app.test_client()

    res = client.post(
        "/process_remote_docs",
        json={
            "bucket_name": "my-demo-project-359019-bucket-noon-html-clean",
            "file_type": "HTML",
        },
    )

    print(res)

#test_create_table()
test_process_remote_docs()
