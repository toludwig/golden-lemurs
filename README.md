# GitHub Classifier by Maxim Schuwalow, Tobias Ludwig & Fabian Richter

## Requirements

Training should only be done natively (not in docker) and GPU-accelerated. GPUs used in training should possess at least 3GB VRAM. As we already deliver a trained model, this should not be necessary. In order to start the server for inference, you should have at least 8GB of available RAM, as our server already requires 5GB to load word embeddings and our model into memory. Our docker image takes up around 10GB of space on disk.

We also need pretrained word embeddings; we used word2vec by Google.
Download this from [here](https://drive.google.com/file/d/0ByJXV7reBQxTa3Zzbk4tVUE0UVE/view?usp=sharing) and save the _compressed_ file into the data directory.

Furthermore, our crawler needs a personal access token with access rights `repo` (full rights, not only public\_repo because of GraphQL).
Please insert this at the marked position in `classification/__init.py__`. GitHub does not allow publication of these.

## Usage

### Classification
We wrote a wrapper script utilizing our classification server for the text files in the given format. You need Python 3 and requests to use it. Before executing it, you need to start the classification server as described in the next parts.

```
pip install requests
./eval.py INPUT OUTPUT
```

Our classifaction of appendix B is in the file `classified`.

### Installation via docker

We built a docker image to easily start up everything included.
You can start it by executing run\_demo.sh
```
./run_demo.sh
```

### Manual installation


Alternatively, you could install our python server as a module and start the server that wraps our classifier:
You would need python 3.5 for that.
```
pip install -e .
github-classify
```

You get raw classifications and repository metadata in JSON at
```
http://localhost:8081/rate/{username}/{reponame}
```

Then, there is our web frontend. You need node & npm for that.
```
cd webapp
npm install -g angular-cli
npm install
ng serve
```
Now, there is a webserver running at localhost:8080.


## Documentation

Our documentation is included in the web frontend.
