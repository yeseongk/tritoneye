Project Lead  - Sameer Kausar
Backend Engineer - Yeseong Kim
Frontend Engineer - Pranay Pant
CSE 145/237D Professor Ryan Kestner
Spring 2016


=Project Overview=
We are creating system that provides live parking availability. This will allow for individuals looking for parking to spend less time searching for spots. This is especially relevant today since most commuter students, faculty and UCSD employees do not have the time to circle around campus hunting for parking. The parking count will be displayed live on a website. 

=Project Approach=
The system would use a network of cameras (one or two per floor) to count the number of cars arriving and leaving. The cameras would be run on a Raspberry Pi and send only the processed data. In other words, the camera will capture the video and the Raspberry Pi will process data locally and send an output (ie, car came or left). We would be using OpenCV and other open source libraries to create an algorithm to count cars and determine what types of spots are open (A, B, S, etc). There are many detailed strategies that have been published but we will design an algorithm that is optimized for UCSD and Raspberry Pi to guarantee reasonable local processing time. With this output sent to a server (using a TCP/IP protocol with some sort of encryption), a website will display the live count of cars per parking lot/structure. Once we have this, we can create an iOS/Android app or integrate it with the current UCSD app.

