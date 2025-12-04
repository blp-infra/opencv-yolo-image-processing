# docker build commands
### Abc image
```docker build -t qmsabc -f Dockerfile .
```
### def image
```docker build -t qmsdef -f Dockerfile2 .```
### latest
```docker build -t latest -f Dockerfile2 .```

# Docker run commands

```docker run -d --name latest -p 8559:8559 -p 8879:8879 -p 8554:8554 -p 8888:8888 -p 8000:8000 imagename:latest```

```docker run -d --name def -p 8555:8555 -p 8889:8889 -p 8554:8554 -p 8888:8888 -p 8000:8000 imagename:qmsdef```



```docker run -d --name AbC -p 8554:8554 -p 8888:8888 -p 8000:8000 imagename:qmsabc```
