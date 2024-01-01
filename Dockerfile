# Use an official Python runtime as a parent image
FROM python:3.10-slim


# Set the working directory in the container
WORKDIR /app

# Copy the main.py script and the entire src/ directory into the container
#COPY main.py ./
# Copy the requirements.txt file into the container
#COPY requirements.txt ./

COPY . .

# Update the package manager and install the necessary packages
#RUN apt-get update && apt-get install -y tk

# Install X11 dependencies
# RUN apt-get update && apt-get install -y \
#     tk \
#     x11-apps \
#     && rm -rf /var/lib/apt/lists/*

# Update package list and install sudo
#RUN apt-get update && apt-get install -y sudo

# Search for the correct package name for Firefox
#RUN apt-cache search firefox

# Install Firefox and X11 dependencies
# RUN apt-get install -y \
#     firefox-esr \
#     tk \
#     libpci3 \
#     x11-apps \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y libx11-6 libxext-dev libxrender-dev libxinerama-dev libxi-dev libxrandr-dev libxcursor-dev libxtst-dev tk-dev && rm -rf /var/lib/apt/lists/*

# Install the project dependencies
RUN pip install -r requirements.txt

ENV DISPLAY=:0
ENV PORT=8080
EXPOSE 8080

# Specify the command to run your main.py script
CMD ["python", "main.py"]


#docker build -t btnm/demogui:0.1 .
#docker run -p 5000:8080 docker_id
#docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix btnm/demogui:0.3 
#192.168.10.195
#docker run -it --rm -e DISPLAY=192.168.10.195:0 -v /tmp/.X11-unix:/tmp/.X11-unix btnm/demogui:0.3 firefox

#docker run -it --rm -p 8080:8080 -e DISPLAY=192.168.10.195:0 -v /tmp/.X11-unix:/tmp/.X11-unix btnm/demogui:0.4
#http://localhost:8080


#set DISPLAY=192.168.10.195:0.0
#docker run -it --rm -e DISPLAY=%DISPLAY% --network="host" --name gui_container btnm/demogui:0.6
#docker run -it --rm -p 8080:8080 -e DISPLAY=$192.168.10.195:0.0 -v /tmp/.X11-unix:/tmp/.X11-unix --network="host" --name gui_container btnm/demogui:0.6
