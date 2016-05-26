class Floor < ActiveRecord::Base

	belongs_to :parking_lot

	def self.adjust_openspots (f)
		if (f != nil)
			cur_spots = f.capacity - f.cars
			if (cur_spots > f.capacity)
				cur_spots = f.capacity
			end

			if (cur_spots < 0)
				cur_spots = 0
			end

			f.open_spots = cur_spots
			puts f.cars
			f.save
		end
	end

	def self.find_spots (f1, f2, direction)
		if(direction == 1) ## car entered
			#means car goes 1->2
			if (f1 != nil)
				f1.cars =  f1.cars - 1
			end
			if (f2 != nil)
				f2.cars =  f2.cars + 1
			end
		else
			if (f1 != nil)
				f1.cars =  f1.cars + 1
			end
			if (f2 != nil)
				f2.cars =  f2.cars - 1
			end
		end
		# Update to DB
		Floor.adjust_openspots(f1)
		Floor.adjust_openspots(f2)
	end
end
