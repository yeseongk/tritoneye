
#!/usr/bin/env ruby
require 'socket'               # Get sockets from stdlib

server = TCPServer.open(3000)  # Socket to listen on port 2000

loop do
 	Thread.start(server.accept) do |client|
		while line = client.gets
			puts line # For debug
			data = line.split(",")
			names = data[0].split("-")
			f1 = Floor.where(name: names[0]).take
			f2 = Floor.where(name: names[1]).take
			if (f1 == nil and f2 == nil)
				next
			end
			in_cars = data[1].to_i
			out_cars = data[2].to_i

			in_cars.times do |cnt|
				Floor.find_spots(f1, f2, 1)
			end
			out_cars.times do |cnt|
				Floor.find_spots(f1, f2, 2)
			end

    end
					
		client.close                 # Disconnect from the client
	end
end
