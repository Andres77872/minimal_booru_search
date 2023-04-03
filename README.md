# A minimal API implementation for image similarity search used in https://findit.moe and https://arz.ai
## For the feature extractor its used https://huggingface.co/SmilingWolf/wd-v1-4-convnext-tagger-v2 and the database https://qdrant.tech/
### About

All images used in the database has been obtained from https://www.gwern.net/Danbooru2021 and has been updated until the id 6060745, all images are  from https://danbooru.donmai.us/

### Usage 

The container will run in the port 6333 por the qdrant database and the port 5000 for the FastAPI

The SW model wil be downloaded automatically in the internal folder */models* and the qdrant databse in */api/qdrant/storage*

The size of SW model its around 400mb and 24gb for the qdrant database so it will take a time

```bash
docker run -it -d -p 6333:6333 -p 5000:5000 --name minimal_search -v /models:/models -v /models/qdrant:/api/qdrant/storage andres77872/minimal_search
```

