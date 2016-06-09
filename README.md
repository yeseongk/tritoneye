Triton Eye: Where's an available parking spot?
==============================================
### Based on video processing and web user interfaces
#### UCSD CSE145/237D Project, Spring 2016
#### CSE 145/237D Professor Ryan Kastner

### Developers
* Project Lead  - Sameer Kausar
* Backend Engineer - Yeseong Kim
* Frontend Engineer - Pranay Pant

Project Overview
================
We are creating system that provides live parking availability. This will allow for individuals looking for parking to spend less time searching for spots. This is especially relevant today since most commuter students, faculty and UCSD employees do not have the time to circle around campus hunting for parking. The parking count will be displayed live on a website. One promising way to reduce the deployment cost is to leverage a computer vision-based vehicle detection on emerging small computing devices such as Raspberry Pi. In this project, our system exploits a network of Raspberry Pi’s with cameras equipped on each floor and counts the number of cars based on OpenCV library. The output is sent to a server over TCP/IP protocols and users can access the information through a website. In our evaluation conducted on a field testing, we show that our systems can report the available parking spots to users on a website by efficient video processing on Raspberry Pi.

Introduction Video
==================

[![Introduction](http://img.youtube.com/vi/lXNUYxQ7uBQ/0.jpg)](https://www.youtube.com/watch?v=lXNUYxQ7uBQ)

Video Tracking Demo
===================
* Hopkins parking structure (UCSD) - Line-based counting

[![Demo1](http://img.youtube.com/vi/LINH5eP4T3M/0.jpg)](https://www.youtube.com/watch?v=LINH5eP4T3M)

* Hopkins parking structure (UCSD) - Area-based counting

[![Demo2](http://img.youtube.com/vi/K-KsFMKGvdQ/0.jpg)](https://www.youtube.com/watch?v=K-KsFMKGvdQ)

* Stocked Video

[![Demo3](http://img.youtube.com/vi/7UajWzdm_yg/0.jpg)](https://www.youtube.com/watch?v=7UajWzdm_yg)


Project Approach
================
In this project, we developed Triton Eye, which utilizes multiple camera-equipped Raspberry Pi’s and a web server that assimilate the information received from the Raspberry Pi’s to server the information to users via their web browsers. The system uses a network of cameras (one per floor) to count the number of cars arriving and leaving. There are many detailed strategies that have been published but we will design an algorithm that is optimized for UCSD and Raspberry Pi to guarantee reasonable local processing time. The cameras would be run on a Raspberry Pi and send only the processed data. In other words, the camera will capture the video and the Raspberry Pi will process data locally and send an output (ie, car came or left). We would be using OpenCV and other open source libraries to create an algorithm to count cars and determine what types of spots are open (A, B, S, etc). With this output sent to a server (using a TCP/IP protocol with some sort of encryption), a website will display the live count of cars per parking lot/structure. The server first performs a parking lot counting algorithm which computes the available number of lots of each floor by using the car counts and the directions received from the Rapsberry Pis. The information is stored into a Sqlite database, thus we can retrieve the real-time parking spot information and show it to the web user interface running on Ruby on Rails.


How to run?
===========
* Backend (Raspberry Pi 2+, OpenCV 3.0.1)

(Actual)      $ python triton_eye.py [-v VIDEO_FILENAME]

(Simulation)  $ python simulation_triton_eye.py -sl LOG_FILENAME -ss SIMULATION_SPEED

* Frontend (Ruby on Rails)

(server)          $ rails runner server.rb

(web app server)  $ rails s -b [IP_ADDRESS or 0.0.0.0 for generic] -p [PORT NUMBER]

What's in repo?
===============

| Component        | Directory           | Description  |
| ---------------- |-------------------| ------------|
| Frontend      | / | Requirement: Ruby on Rails |
| Backend      | /src      |   Requirement: OpenCV 3.0.1 |
| Test code for OpenCV | /test_src      |    Usable to check the valid setup of Raspberry Pi |
| Sample video | /sample_video | Include stocked videos and field testing video recorded in UCSD |
| Sample log | /sample_log | Input files for the traffic simulator |
