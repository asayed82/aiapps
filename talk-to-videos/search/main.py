import json, os
from flask import Flask, request, render_template, flash
from langchain_community.vectorstores.pgvector import PGVector
from collections import defaultdict
from utils import database, config, embedai


settings = config.Settings()

db = database.Client(settings=settings)

pgv =  PGVector(
        collection_name=db.video_collection,
        connection_string=db.get_lc_pgv_connection_string(),
        embedding_function=embedai.lc_vai_embeddings
    )

def create_app():
    # Dev only: run "python main.py" and open http://localhost:8080
    
    app = Flask(__name__)

    @app.route("/", methods=("GET", "POST"))
    def index():
        return render_template("index.html")


    @app.route("/videos/query", methods=("GET", "POST"))
    async def videos_query():
        results = []
        txt_query=""

        if request.method == "POST":
            txt_query = request.form["txt_query"]

            print(f"search query= {txt_query}")

            if not txt_query:
                flash("search query is required")

            matches = pgv.similarity_search_with_relevance_scores(query=txt_query, k=10)

            results = defaultdict(lambda: defaultdict(list))

            for doc, score in matches:

                content = json.loads(doc.page_content)
                doc.metadata["description"]=content["description"]
                doc.metadata["transcript"]=content["transcript"]
                doc.metadata["labels"]=content["labels"]
                doc.metadata["score"]=score

                results[doc.metadata["video_id"]]["segments"].append(doc)

            videos = await db.list_videos(tuple(results.keys()))

            for video in videos:
                results[video["video_id"]]["video_details"].append(video)

        return render_template("index.html", results=results, txt_query=txt_query)
    
    return app

app = create_app()

if __name__ == "__main__":
    print(f"Starting video search app with following settings : {settings}")
    app.run(host="0.0.0.0", port=int(settings.port), debug=True)

