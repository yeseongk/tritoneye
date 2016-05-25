class CreateParkingLots < ActiveRecord::Migration
  def change
    create_table :parking_lots do |t|
      t.string :name

      t.timestamps null: false
    end
  end
end
