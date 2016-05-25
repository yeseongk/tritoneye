class AddOpenSpotsFieldToFloor < ActiveRecord::Migration

	def change
		add_column :floors, :open_spots, :integer, default: 0
	end

end
