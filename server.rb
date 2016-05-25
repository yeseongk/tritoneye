
#!/usr/bin/env ruby
require 'socket'               # Get sockets from stdlib

server = TCPServer.open(3000)  # Socket to listen on port 2000
client = server.accept       # Wait for a client to connect
while line = client.gets
 	puts line

  	data = line.split(",")

  	if  ((f = Floor.find_by(name: data[0])) == nil)
  		next;
  	end

  	Floor.find_spots(f, data[2].to_i)

end
client.close                 # Disconnect from the client





