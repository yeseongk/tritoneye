Triton Eye: Where's an available parking spot?
Based on video processing and web user interfaces

UCSD CSE145/237D Project, Spring 2016
CSE 145/237D Professor Ryan Kestner

Project Lead  - Sameer Kausar
Backend Engineer - Yeseong Kim
Frontend Engineer - Pranay Pant

You can find more deails in our wiki, including
* Working Video!
* How to execute the program including opencv-based vechile tracking application running on Raspberry Pi, and webserver program running on Ruby on Rails
* How to configure the tracking algorithm
* Technical details used in our project

Project Overview:
We are creating system that provides live parking availability. This will allow for individuals looking for parking to spend less time searching for spots. This is especially relevant today since most commuter students, faculty and UCSD employees do not have the time to circle around campus hunting for parking. The parking count will be displayed live on a website. One promising way to reduce the deployment cost is to leverage a computer vision-based vehicle detection on emerging small computing devices such as Raspberry Pi. In this project, our system exploits a network of Raspberry Pi’s with cameras equipped on each floor and counts the number of cars based on OpenCV library. The output is sent to a server over TCP/IP protocols and users can access the information through a website. In our evaluation conducted on a field testing, we show that our systems can report the available parking spots to users on a website by efficient video processing on Raspberry Pi.

Project Approach:
In this project, we developed Triton Eye, which utilizes multiple camera-equipped Raspberry Pi’s and a web server that assimilate the information received from the Raspberry Pi’s to server the information to users via their web browsers. The system uses a network of cameras (one per floor) to count the number of cars arriving and leaving. There are many detailed strategies that have been published but we will design an algorithm that is optimized for UCSD and Raspberry Pi to guarantee reasonable local processing time. The cameras would be run on a Raspberry Pi and send only the processed data. In other words, the camera will capture the video and the Raspberry Pi will process data locally and send an output (ie, car came or left). We would be using OpenCV and other open source libraries to create an algorithm to count cars and determine what types of spots are open (A, B, S, etc). With this output sent to a server (using a TCP/IP protocol with some sort of encryption), a website will display the live count of cars per parking lot/structure. The server first performs a parking lot counting algorithm which computes the available number of lots of each floor by using the car counts and the directions received from the Rapsberry Pis. The information is stored into a Sqlite database, thus we can retrieve the real-time parking spot information and show it to the web user interface running on Ruby on Rails.
