# GitHub Classifier by Maxim Schuwalow, Tobias Ludwig & Fabian Richter

## System Requirements

Training should only be done natively (not in docker) and GPU-accelerated. GPUs used in training should possess at least 3GB VRAM. As we already deliver a trained model, this should not be necessary. In order to start the server for inference, you should have at least 8GB of available RAM, as our server already requires 5GB to load word embeddings and our model into memory. Our docker image takes up around 10GB of space on disk.

## Usage

### Classification
We wrote a wrapper script utilizing our classification server for the text files in the given format. You need Python 3 and requests to use it. Before executing it, you need to start the classification server as described in the next parts.

```
pip install requests
./eval.py INPUT OUTPUT
```

### Installation via docker

We built a docker image to easily start up everything included.
You can start it by executing run_demo.sh
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

Our documentation is included
in the web frontend.
