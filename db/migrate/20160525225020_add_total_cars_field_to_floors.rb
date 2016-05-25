class AddTotalCarsFieldToFloors < ActiveRecord::Migration
  def change
  	add_column :floors, :cars, :integer, default: 0 
  end
end
